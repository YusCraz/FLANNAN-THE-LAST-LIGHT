"""Serve the browser game and manage local development sessions."""

import asyncio
import logging
import secrets
from contextlib import asynccontextmanager, suppress
from dataclasses import dataclass
from pathlib import Path
from time import monotonic

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field
from starlette.middleware.trustedhost import TrustedHostMiddleware

from .session import FastSession
from .story import SCENES


WEB_DIR = Path(__file__).resolve().parent / "web"
COOKIE_NAME = "flannan_session"

# Bound local resource usage and clean up abandoned background workers.
SESSION_TTL = 30 * 60
MAX_SESSIONS = 8


@dataclass
class GameRecord:
    """Store one player's game and the current turn number."""

    game: FastSession
    revision: int
    touched: float


class ChoiceRequest(BaseModel):
    """Accept only a keyword and the turn the browser is displaying."""

    model_config = ConfigDict(extra="forbid", strict=True)

    keyword: str = Field(min_length=1, max_length=32)
    revision: int = Field(ge=0)


sessions: dict[str, GameRecord] = {}


def remove_session(session_id):
    """Remove a session and stop future AI preparation."""

    record = sessions.pop(session_id, None)

    if record is not None:
        record.game.close()


def remove_expired_sessions():
    """Expire sessions after thirty minutes without browser activity."""

    now = monotonic()

    for session_id, record in list(sessions.items()):
        if now - record.touched > SESSION_TTL:
            remove_session(session_id)


async def cleanup_loop():
    """Periodically clean up without blocking request handling."""

    while True:
        await asyncio.sleep(30)
        remove_expired_sessions()


@asynccontextmanager
async def lifespan(app):
    """Start cleanup and close sessions when the server stops."""

    logging.basicConfig(
        filename="flannan.log",
        encoding="utf-8",
        level=logging.WARNING,
        format="%(asctime)s %(levelname)s: %(message)s",
    )

    cleanup = asyncio.create_task(cleanup_loop())

    try:
        yield
    finally:
        cleanup.cancel()

        with suppress(asyncio.CancelledError):
            await cleanup

        for session_id in list(sessions):
            remove_session(session_id)


app = FastAPI(
    title="FLANNAN",
    lifespan=lifespan,
)

# This configuration intentionally serves local development only.
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["127.0.0.1", "localhost", "testserver"],
)

# Expose only frontend assets, never the project root or .env.
app.mount(
    "/static",
    StaticFiles(directory=WEB_DIR),
    name="static",
)


def check_browser_request(request):
    """Require our same-origin browser request for state changes."""

    if request.headers.get("X-Flannan-Client") != "browser":
        raise HTTPException(403, "Missing browser request header.")

    origin = request.headers.get("origin")
    expected_origin = str(request.base_url).rstrip("/")

    if origin is not None and origin != expected_origin:
        raise HTTPException(403, "Cross-origin request rejected.")


def get_record(request):
    """Find the session identified by the browser's private cookie."""

    remove_expired_sessions()

    session_id = request.cookies.get(COOKIE_NAME)
    record = sessions.get(session_id)

    if record is None:
        raise HTTPException(404, "Session expired. Start a new game.")

    record.touched = monotonic()
    return record


def keep_authored_narration(game):
    """Keep story text consistent while retaining AI presentation cues."""

    narration = SCENES[game.state["scene"]]["narration"]
    game.presentation["narration"] = narration

    # Ensure context records the text actually shown in the browser.
    history = game.state.get("director_history", [])

    if history:
        history[-1]["narration"] = narration


def scene_response(record):
    """Return only the information needed to display the current scene."""

    game = record.game
    scene_id = game.state["scene"]
    scene = SCENES[scene_id]

    return {
        "revision": record.revision,
        "scene_id": scene_id,
        "title": scene["title"],
        "narration": game.presentation["narration"],
        "choices": [
            {"keyword": keyword, "label": choice["label"]}
            for keyword, choice in scene["choices"].items()
        ],
        "ending": not bool(scene["choices"]),
        "cues": {
            "delivery": game.presentation["delivery"],
            "sound": game.presentation["sound"],
            "effect": game.presentation["effect"],
        },
    }


@app.get("/")
async def home():
    """Serve the game's page."""

    return FileResponse(
        WEB_DIR / "index.html",
        headers={"Cache-Control": "no-store"},
    )


@app.post("/api/game")
async def start_game(request: Request, response: Response):
    """Create a game or replace this browser's previous game."""

    check_browser_request(request)
    remove_expired_sessions()

    previous_id = request.cookies.get(COOKIE_NAME)

    if previous_id in sessions:
        remove_session(previous_id)

    if len(sessions) >= MAX_SESSIONS:
        raise HTTPException(503, "Local session limit reached. Try again later.")

    game = FastSession()
    keep_authored_narration(game)

    session_id = secrets.token_urlsafe(32)
    record = GameRecord(game=game, revision=0, touched=monotonic())
    sessions[session_id] = record

    game.prepare_choices()

    response.set_cookie(
        COOKIE_NAME,
        session_id,
        httponly=True,
        samesite="strict",
        secure=request.url.scheme == "https",
        path="/",
    )
    response.headers["Cache-Control"] = "no-store"

    return scene_response(record)


@app.get("/api/game")
async def current_game(request: Request, response: Response):
    """Recover the current scene after a page refresh."""

    record = get_record(request)
    response.headers["Cache-Control"] = "no-store"
    return scene_response(record)


@app.post("/api/game/choice")
async def choose(
    choice: ChoiceRequest,
    request: Request,
    response: Response,
):
    """Validate and apply exactly one choice to the current turn."""

    check_browser_request(request)
    record = get_record(request)

    # Reject double clicks or submissions from an outdated browser tab.
    if choice.revision != record.revision:
        raise HTTPException(409, "The scene changed. Refresh the current scene.")

    scene = SCENES[record.game.state["scene"]]

    if not scene["choices"]:
        raise HTTPException(409, "This playthrough has ended.")

    if not record.game.choose(choice.keyword):
        raise HTTPException(400, "That choice is not available here.")

    record.revision += 1
    keep_authored_narration(record.game)

    if SCENES[record.game.state["scene"]]["choices"]:
        record.game.prepare_choices()
    else:
        # Keep the ending readable, but stop the session's AI worker.
        record.game.close()

    response.headers["Cache-Control"] = "no-store"
    return scene_response(record)


@app.delete("/api/game")
async def end_game(request: Request, response: Response):
    """End this browser's session and clear its cookie."""

    check_browser_request(request)
    remove_session(request.cookies.get(COOKIE_NAME))

    response.delete_cookie(COOKIE_NAME, path="/")
    response.headers["Cache-Control"] = "no-store"

    return {"ended": True}