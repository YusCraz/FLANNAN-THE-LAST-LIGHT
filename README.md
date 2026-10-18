FLANNAN: THE LAST LIGHT
Three keepers. No answer. One light that should stay dark.
A playable browser horror mystery with a Python backend, illustrated first-person scenes, atmospheric audio, and an AI presentation director.
Play the demo · Source code
Status: Playable portfolio demo; further development planned.
Hosted on Render's free plan. The first visit after inactivity may take about a minute to load. Sessions are temporary and reset when the server restarts.

The story
Three lighthouse keepers have disappeared. You arrive as a relief keeper to investigate the station and restore its light—if it is safe.
Someone answers your radio. They know why you came.
Explore the island, follow the evidence, and decide which voices to trust. This is a fictional supernatural story inspired by the Flannan Isles disappearance, not a historical reconstruction.
What works today
- 18 authored scenes and three endings connected by player choices.
- Illustrated scene backgrounds with crossfades and next-scene image preloading.
- Looping horror music, synthesized sea and wind ambience, and separate volume controls.
- Context-aware AI presentation cues prepared in the background.
- Immediate scripted fallback whenever AI direction is unavailable or unfinished.
- Browser sessions, server-side choice validation, and revision checks that reject stale submissions.
- A terminal version alongside the browser game.
- A separate Rive CLI fog-animation prototype in animations/.
The Rive prototype is not yet integrated into the live browser game.
How the AI works
The story engine owns scene transitions, available choices, and gameplay state. The model does not invent branches or choose the player's actions.
While the player reads a scene, the session simulates its available choices using independent copies of game state. One Hugging Face request prepares presentation directions for all possible destinations.
The director receives recent choices, gameplay values, destination narration, and recent presentation cues. It returns structured JSON containing delivery, sound, effect, and an optional short atmospheric line.
Pydantic validates the response structure. Additional checks require exactly one result per choice and restrict sound and effect names to each scene's allowed values. Late responses are discarded when the player moves on.
When the player selects a choice, the game uses a ready direction or immediately falls back to the authored presentation. Gameplay never waits for an AI request to finish.
The browser preserves authored narration and uses the presentation cues. The terminal version can also show the optional atmospheric line. Structural validation does not guarantee the literary quality of generated text.
AI engineering concepts used: context management, structured outputs, application-level validation, batched inference, background execution, stale-result protection, and graceful fallback. RAG and model training are not implemented.
Stack
Part	Technology
Backend	Python, FastAPI, Uvicorn
Frontend	HTML, CSS, JavaScript, Web Audio API
AI integration	Hugging Face Inference Providers, HTTPX
Configured model	Qwen/Qwen3-Next-80B-A3B-Instruct:deepinfra
Response validation	Pydantic
Animation prototype	Rive CLI and RML
Hosting	Render


Run locally
Requires Python 3.11 or newer. Commands below use Windows PowerShell.
git clone https://github.com/YusCraz/FLANNAN-THE-LAST-LIGHT.git
Set-Location FLANNAN-THE-LAST-LIGHT
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
AI is optional. To enable it, create .env in the project root:
HF_TOKEN=your_hugging_face_token
HF_MODEL=Qwen/Qwen3-Next-80B-A3B-Instruct:deepinfra
Use a token with permission to call Inference Providers. Provider availability, credits, and rate limits apply separately from hosting. Without configuration, the authored game remains playable.
Start the browser game:
.\.venv\Scripts\python.exe -m uvicorn flannan.api:app --host 127.0.0.1 --port 8000
Open http://127.0.0.1:8000. Music starts after user interaction; check the sound controls if muted.
Run the terminal version:
.\.venv\Scripts\python.exe -m flannan.cli
Keep .env private. It is ignored by Git; API credentials belong on the server, never in browser JavaScript.
Project structure
src/flannan/
  state.py       Initial player state
  story.py       Authored scenes, choices, and endings
  engine.py      Choice validation and state transitions
  director.py    Hugging Face requests and response validation
  session.py     Background preparation and immediate fallback
  api.py         Browser API, cookies, and session lifecycle
  cli.py         Terminal interface
  web/           HTML, CSS, JavaScript, scene images, and audio
animations/
  lighthouse/          Rive fog source and generator
  lighthouse-preview/  Separate artwork-and-fog preview
Deploy on Render
Create a Python Web Service connected to this repository.
Setting	Value
Branch	main
Root Directory	Leave empty
Build Command	pip install -e .
Instance Type	Free
Health Check Path	/health


Start Command (enter in Render, not local PowerShell):
uvicorn flannan.api:app --host 0.0.0.0 --port $PORT --workers 1 --proxy-headers --forwarded-allow-ips '*'
Add HF_TOKEN and HF_MODEL as private environment variables to enable AI direction. The app accepts Render's automatically provided RENDER_EXTERNAL_HOSTNAME. Keep one worker because sessions currently live in process memory.
Limitations and next steps
This is a small portfolio demo, not a production service. Sessions expire after 30 minutes without API activity; the backend currently allows eight simultaneous sessions. Restarting or redeploying clears progress. Render's free service can sleep after inactivity.
AI cues are optional and may fall back because of latency, provider errors, or exhausted credits. Scene effects are limited to what the frontend implements; a cue name alone does not create an animation.
Planned improvements:
- Integrate the Rive fog prototype into the browser experience.
- Add persistent sessions and public-API rate limiting.
- Expand automated coverage for the API and background worker.
- Review mobile layouts, accessibility, and audio balance across devices.
Credits
Created by Aayush Lohani.
Scene illustrations were created with AI assistance. The project began during the Rive Halloween Challenge 2026 and continues as an independent portfolio project.
Music: “Darkest Child” — Kevin MacLeod, Incompetech, licensed under Creative Commons Attribution 4.0. Playback loops and volume fades are applied. Music attribution is also available in the game's sound controls.
