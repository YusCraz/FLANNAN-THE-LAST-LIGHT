# FLANNAN: THE LAST LIGHT

### [▶ Play the Live Demo](https://flannan-the-last-light.onrender.com/)

> The free server may take about a minute to wake up after inactivity.

An interactive horror mystery inspired by the Flannan Isles lighthouse disappearance. Investigate three missing keepers through illustrated first-person scenes, branching choices, and atmospheric audio—with an AI director adjusting the presentation.

**Status:** Playable demo · Work in progress

## The Story

Three lighthouse keepers have stopped answering messages.

You arrive to investigate the station and restore the light—if it is safe.

Then someone answers your radio.

Explore the island, follow the evidence, and decide which voices to trust. Your choices lead to three possible endings.

*This is a fictional supernatural story, not a historical reconstruction.*

## Features

- **18 illustrated scenes** with branching choices and three endings.
- **Atmospheric audio:** horror music, synthesized wind, and sea ambience.
- **Scene transitions** with background crossfades and image preloading.
- **AI presentation direction** using Qwen through Hugging Face.
- **Immediate gameplay:** authored fallback when AI responses are unavailable or unfinished.
- **Server-side validation** of player choices and scene revisions.
- **Browser and terminal interfaces.**
- **Rive fog-animation prototype**, awaiting browser integration.

## How the AI Works

The Python story engine controls the plot, available choices, and game state.

While the player reads, a background worker prepares AI presentation cues for the possible next scenes. The model receives relevant context, including recent choices, tension, and previous cues.

Responses are validated with Pydantic and checked against scene-specific sound and effect restrictions.

When the player chooses:

1. The engine validates the choice and updates the state.
2. Prepared AI cues are used if available.
3. Otherwise, the authored presentation appears immediately.

The browser preserves the written narration. AI influences presentation rather than inventing new story branches.

**Concepts implemented:** context management, structured outputs, batched inference, background processing, response validation, stale-result protection, and graceful fallback.

## Technology

| Component | Tools |
|---|---|
| Backend | Python, FastAPI, Uvicorn |
| Frontend | HTML, CSS, JavaScript |
| Audio | Web Audio API and MP3 playback |
| AI | Qwen through Hugging Face Inference Providers |
| Validation | Pydantic |
| HTTP client | HTTPX |
| Animation prototype | Rive CLI and RML |
| Hosting | Render |

## Run Locally

Requires **Python 3.11+**.

### 1. Clone and install

Run in Windows PowerShell:

```powershell
git clone https://github.com/YusCraz/FLANNAN-THE-LAST-LIGHT.git
Set-Location FLANNAN-THE-LAST-LIGHT

py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
```

### 2. Configure AI — optional

Create a `.env` file in the project root:

```dotenv
HF_TOKEN=your_hugging_face_token
HF_MODEL=Qwen/Qwen3-Next-80B-A3B-Instruct:deepinfra
```

The token needs permission to call Inference Providers. Provider availability, credits, and rate limits apply.

Without AI configuration, the scripted game remains playable.

**Never commit your `.env` file or put API tokens in frontend code.**

### 3. Start the website

```powershell
.\.venv\Scripts\python.exe -m uvicorn flannan.api:app --host 127.0.0.1 --port 8000
```

Open **http://127.0.0.1:8000**.

### Terminal version

```powershell
.\.venv\Scripts\python.exe -m flannan.cli
```

## Project Structure

```text
src/flannan/
├── state.py       # Initial player state
├── story.py       # Scenes, choices, and endings
├── engine.py      # Choice validation and state updates
├── director.py    # AI requests and response validation
├── session.py     # Background preparation and fallback
├── api.py         # Browser API and session management
├── cli.py         # Terminal interface
└── web/           # Website, illustrations, and audio

animations/
├── lighthouse/          # Rive fog source and generator
└── lighthouse-preview/  # Separate animation preview
```

## Deployment

The frontend and Python backend are hosted together on **Render**.

| Setting | Value |
|---|---|
| Build command | `pip install -e .` |
| Health check | `/health` |
| Environment variables | `HF_TOKEN`, `HF_MODEL` |

Start command:

```bash
uvicorn flannan.api:app --host 0.0.0.0 --port $PORT --workers 1 --proxy-headers --forwarded-allow-ips '*'
```

## Current Limitations

- Render's free service sleeps after inactivity.
- Sessions are stored in memory and reset on server restart.
- Sessions expire after 30 minutes without API activity.
- The backend currently allows eight simultaneous sessions.
- AI direction depends on provider availability and credits.
- Rive animation is a separate prototype, not integrated into the live game.
- RAG and model training are not implemented.

## Next Steps

- Integrate Rive animations into the browser.
- Add persistent game sessions.
- Add public-API rate limiting.
- Expand automated testing.
- Improve mobile layouts and accessibility.

## Credits

Created by [Aayush Lohani](https://github.com/YusCraz).

Scene illustrations were created with AI assistance.

Music: **“Darkest Child” by Kevin MacLeod**  
Source: [Incompetech](https://incompetech.com/music/royalty-free/index.html?Search=Search&isrc=USUAN1100783)  
License: [Creative Commons Attribution 4.0](https://creativecommons.org/licenses/by/4.0/)  
Modifications: looping playback and volume fades.

Originally started during the Rive Halloween Challenge 2026; continuing as an independent portfolio project.
