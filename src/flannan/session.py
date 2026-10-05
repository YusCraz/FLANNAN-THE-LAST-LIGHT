"""Provide instant transitions with batched background AI direction."""

from copy import deepcopy
from queue import Empty, Queue
from threading import Event, Lock, Thread

from .director import AIDirector
from .engine import apply_choice
from .state import create_game_state
from .story import SCENES


def scripted_presentation(game_state):
    """Build an immediate presentation from the authored story."""

    scene_id = game_state["scene"]

    return {
        "scene_id": scene_id,
        "narration": SCENES[scene_id]["narration"],
        "delivery": "steady",
        "sound": "silence",
        "effect": "none",
        "source": "scripted",
    }


def build_candidates(game_state):
    """Simulate each available choice without changing the real state."""

    candidates = {}
    choices = SCENES[game_state["scene"]]["choices"]

    for keyword in choices:
        # Each potential branch gets independent game memory.
        candidate = deepcopy(game_state)

        if apply_choice(candidate, keyword):
            candidates[keyword] = candidate

    return candidates


class FastSession:
    """Manage gameplay and prepare AI decisions in the background."""

    def __init__(self):
        # Start with authored narration so the opening appears immediately.
        self.state = create_game_state()
        self.state["director_history"] = []

        self.presentation = scripted_presentation(self.state)
        self._record_presentation()

        # One worker processes API requests sequentially.
        self._jobs = Queue()
        self._ready = {}
        self._lock = Lock()
        self._stop = Event()

        # This number identifies the current decision point.
        self._generation = 0

        # Background work must not prevent the player from exiting.
        self._worker = Thread(
            target=self._prepare_in_background,
            daemon=True,
        )
        self._worker.start()

    def _record_presentation(self):
        """Record only the presentation actually shown to the player."""

        self.state["director_history"].append(
            deepcopy(self.presentation)
        )

    def prepare_choices(self):
        """Queue one AI request covering all current choices."""

        # Invalidate results from the previous decision point.
        with self._lock:
            self._generation += 1
            generation = self._generation
            self._ready.clear()

        # Remove old requests that have not started.
        while True:
            try:
                self._jobs.get_nowait()
            except Empty:
                break

        # The worker receives independent copies of game memory.
        snapshot = deepcopy(self.state)
        candidates = build_candidates(snapshot)

        if candidates:
            self._jobs.put((generation, snapshot, candidates))

    def _prepare_in_background(self):
        """Use one API client to prepare complete batches."""

        director = None

        try:
            director = AIDirector()

            while not self._stop.is_set():
                try:
                    generation, snapshot, candidates = self._jobs.get(
                        timeout=0.2
                    )
                except Empty:
                    continue

                # Skip queued work if the player has already moved on.
                with self._lock:
                    if generation != self._generation:
                        continue

                if self._stop.is_set():
                    break

                directions = director.direct_batch(snapshot, candidates)

                # Never attach a late response to a newer scene.
                with self._lock:
                    if (
                        generation == self._generation
                        and not self._stop.is_set()
                    ):
                        self._ready = directions

        finally:
            # The worker owns and closes its HTTP client.
            if director is not None:
                director.close()

    def choose(self, user_choice):
        """Apply a valid choice immediately, without waiting for AI."""

        keyword = user_choice.strip().upper()
        candidate = deepcopy(self.state)

        # Invalid choices leave the real state unchanged.
        if not apply_choice(candidate, keyword):
            return False

        with self._lock:
            direction = self._ready.get(keyword)

            # Invalidate unfinished work for this decision point.
            self._generation += 1
            self._ready.clear()

        # Authored narration is always available as the instant fallback.
        presentation = scripted_presentation(candidate)

        if direction is not None:
            presentation["delivery"] = direction["delivery"]
            presentation["sound"] = direction["sound"]
            presentation["effect"] = direction["effect"]
            presentation["source"] = "ai"

            # Add the optional short line without replacing the story.
            line = direction["adaptive_line"].strip()

            if line:
                presentation["narration"] += "\n\n" + line

        # Commit the selected state and record what was displayed.
        self.state = candidate
        self.presentation = presentation
        self._record_presentation()
        return True

    def close(self):
        """Stop future preparation without blocking the player's exit."""

        self._stop.set()

        with self._lock:
            self._generation += 1
            self._ready.clear()