"use strict";

/* Recorded soundtrack plus soft procedural sea and wind. */
const soundEngine = (() => {
  const TRACK = "/static/assets/audio/horror-theme.mp3";

  // Each scene specifies sea level, wind level, and musical intensity.
  const profiles = {
    missing_report: [0.28, 0.16, 0.12],
    case_report: [0.20, 0.10, 0.12],
    captain_warning: [0.28, 0.16, 0.22],
    crossing: [0.48, 0.30, 0.28],
    radio_identity: [0.30, 0.26, 0.38],
    lighthouse_exterior: [0.22, 0.35, 0.42],
    upper_window: [0.10, 0.20, 0.64],
    radio_warning: [0.15, 0.28, 0.52],
    entry_hall: [0.035, 0.05, 0.36],
    keeper_notebook: [0.02, 0.03, 0.46],
    west_landing: [0.55, 0.35, 0.64],
    captain_call: [0.40, 0.30, 0.70],
    staircase: [0.015, 0.04, 0.70],
    door_voice: [0, 0.025, 0.76],
    lantern_room: [0.08, 0.20, 0.84],
    ending_departure: [0.35, 0.18, 0.22],
    ending_dark: [0, 0.025, 0.30],
    ending_beacon: [0.15, 0.22, 0.90],
  };

  let ctx;
  let master;
  let musicGain;
  let seaGain;
  let windGain;

  let scene = null;
  let muted = false;
  let musicVolume = 0.35;
  let atmosphereVolume = 0.30;
  let errorMessage = "";
  let playAttempt = 0;

  const track = new Audio();
  track.src = TRACK;
  track.loop = true;
  track.preload = "none";

  // Audio controls remain usable during story requests.
  const controls = document.createElement("div");
  controls.className = "audio-controls";

  const button = document.createElement("button");
  button.type = "button";
  button.className = "text-button";
  button.dataset.audioControl = "true";
  button.textContent = "Enable sound";
  controls.append(button);

  function addSlider(name, initial, onChange) {
    const label = document.createElement("label");
    label.textContent = name + " ";

    const input = document.createElement("input");
    input.type = "range";
    input.min = "0";
    input.max = "100";
    input.value = String(initial);
    input.setAttribute("aria-label", name + " volume");

    input.addEventListener("input", () => {
      onChange(Number(input.value) / 100);
      mix();
    });

    label.append(input);
    controls.append(label);
  }

  addSlider("Music", 35, (value) => {
    musicVolume = value;
  });

  addSlider("Sea / wind", 30, (value) => {
    atmosphereVolume = value;
  });

  const status = document.createElement("span");
  status.className = "audio-status";
  status.setAttribute("role", "status");
  controls.append(status);

  document.querySelector(".topbar").append(controls);

  // Include the soundtrack's attribution in the game.
  const credit = document.createElement("details");
  credit.className = "music-credit";

  const summary = document.createElement("summary");
  summary.textContent = "Music credit";

  const description = document.createElement("p");
  description.append("“Darkest Child” — Kevin MacLeod. ");

  for (const [text, url] of [
    [
      "Original track",
      "https://incompetech.com/music/royalty-free/index.html?Search=Search&isrc=USUAN1100783",
    ],
    [
      "CC BY 4.0",
      "https://creativecommons.org/licenses/by/4.0/",
    ],
  ]) {
    const link = document.createElement("a");
    link.textContent = text;
    link.href = url;
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    description.append(link, " · ");
  }

  description.append("Playback loops and volume fades applied.");
  credit.append(summary, description);
  document.querySelector("footer").append(credit);

  // Style the added controls without replacing your existing CSS.
  const style = document.createElement("style");
  style.textContent = `
    .topbar,
    footer {
      flex-wrap: wrap;
    }

    .audio-controls {
      display: flex;
      gap: 12px;
      align-items: center;
      flex-wrap: wrap;
    }

    .audio-controls label {
      display: flex;
      gap: 7px;
      align-items: center;
      font: 11px Arial, sans-serif;
      color: #ddc4c9;
    }

    .audio-controls input {
      width: 70px;
      accent-color: #bc3047;
    }

    .audio-status {
      font: 11px Arial, sans-serif;
      color: #e8c9c9;
    }

    .music-credit {
      font: 11px Arial, sans-serif;
      letter-spacing: normal;
      line-height: 1.6;
    }

    .music-credit summary {
      cursor: pointer;
    }

    .music-credit p {
      max-width: 420px;
      margin: 6px 0;
    }

    .music-credit a {
      color: #ecc4c9;
    }

    @media (max-width: 600px) {
      .audio-controls {
        gap: 8px;
      }

      .audio-controls input {
        width: 58px;
      }
    }
  `;
  document.head.append(style);

  function ramp(param, value, seconds = 1.5) {
    param.cancelScheduledValues(ctx.currentTime);
    param.setTargetAtTime(
      value,
      ctx.currentTime,
      Math.max(0.02, seconds / 3)
    );
  }

  function build() {
    const Context = window.AudioContext || window.webkitAudioContext;

    if (!Context) {
      throw new Error("This browser does not support game audio.");
    }

    ctx = new Context();

    master = ctx.createGain();
    master.gain.value = 0;
    master.connect(ctx.destination);

    musicGain = ctx.createGain();
    musicGain.gain.value = 0;

    ctx.createMediaElementSource(track)
      .connect(musicGain)
      .connect(master);

    // Generate soft noise, filtering out rumble and sharp hiss.
    const buffer = ctx.createBuffer(
      1,
      ctx.sampleRate * 8,
      ctx.sampleRate
    );

    const samples = buffer.getChannelData(0);
    const edge = ctx.sampleRate * 0.04;
    let smooth = 0;

    for (let i = 0; i < samples.length; i++) {
      smooth = smooth * 0.92 + (Math.random() * 2 - 1) * 0.08;

      const fade = Math.min(
        1,
        i / edge,
        (samples.length - 1 - i) / edge
      );

      samples[i] = smooth * 2 * fade;
    }

    function environment(highCut, waveSpeed) {
      const source = ctx.createBufferSource();
      source.buffer = buffer;
      source.loop = true;

      const low = ctx.createBiquadFilter();
      low.type = "lowpass";
      low.frequency.value = highCut;
      low.Q.value = 0.5;

      const high = ctx.createBiquadFilter();
      high.type = "highpass";
      high.frequency.value = 130;
      high.Q.value = 0.5;

      const swell = ctx.createGain();
      swell.gain.value = 0.65;

      const level = ctx.createGain();
      level.gain.value = 0;

      source
        .connect(high)
        .connect(low)
        .connect(swell)
        .connect(level)
        .connect(master);

      // These slow oscillators control volume; they are not audible tones.
      const lfo = ctx.createOscillator();
      lfo.frequency.value = waveSpeed;

      const depth = ctx.createGain();
      depth.gain.value = 0.25;

      lfo.connect(depth).connect(swell.gain);

      source.start();
      lfo.start();

      return level;
    }

    seaGain = environment(950, 0.12);
    windGain = environment(1500, 0.065);

    ctx.onstatechange = mix;
  }

  function mix() {
    if (!ctx || !master || !windGain) return;

    const audible = scene && !muted && !document.hidden;
    ramp(master.gain, audible ? 0.65 : 0, 0.2);

    const [sea, wind, tension] =
      profiles[scene?.scene_id] || [0, 0, 0];

    // AI cues make small adjustments to the authored scene mix.
    const quiet = scene?.cues?.sound === "silence" ? 0.5 : 1;
    const seaBoost = scene?.cues?.sound === "ocean" ? 1.1 : 1;

    ramp(
      seaGain.gain,
      sea * seaBoost * atmosphereVolume * quiet
    );

    ramp(
      windGain.gain,
      wind * atmosphereVolume * quiet
    );

    const urgent = scene?.cues?.delivery === "urgent" ? 0.08 : 0;

    ramp(
      musicGain.gain,
      musicVolume * (0.35 + tension * 0.3 + urgent),
      2
    );

    button.textContent =
      ctx.state !== "running"
        ? "Enable sound"
        : muted
          ? "Unmute sound"
          : "Mute sound";

    status.textContent = errorMessage;
  }

  function playMusic() {
    if (!ctx || muted || document.hidden) return;

    if (track.error) {
      track.load();
      errorMessage = "";
    }

    const attempt = ++playAttempt;
    const result = track.play();

    if (result) {
      result
        .then(() => {
          if (attempt === playAttempt) {
            errorMessage = "";
            mix();
          }
        })
        .catch((error) => {
          if (
            attempt !== playAttempt ||
            error.name === "AbortError"
          ) {
            return;
          }

          errorMessage =
            error.name === "NotAllowedError"
              ? "Click Enable sound to start music."
              : "Music unavailable — check horror-theme.mp3.";

          mix();
        });
    }
  }

  function unlock() {
    try {
      if (!ctx) build();

      // Start audio within the user click, before awaiting the server.
      ctx.resume()
        .then(mix)
        .catch(() => {
          status.textContent = "Click Enable sound to retry.";
        });

      playMusic();
    } catch (error) {
      status.textContent = error.message;
    }
  }

  function enter(next) {
    scene = next;
    mix();

    // Continue the same track instead of restarting at every choice.
    if (ctx && ctx.state === "running" && track.paused) {
      playMusic();
    }
  }

  function stop() {
    scene = null;
    playAttempt++;
    track.pause();
    mix();
  }

  button.addEventListener("click", () => {
    if (!ctx || ctx.state !== "running") {
      unlock();
    } else {
      muted = !muted;

      if (muted) {
        playAttempt++;
        track.pause();
      } else {
        unlock();
      }

      mix();
    }
  });

  track.addEventListener("error", () => {
    errorMessage = "Music unavailable — check horror-theme.mp3.";
    status.textContent = errorMessage;
  });

  // Silence the game when the player switches browser tabs.
  document.addEventListener("visibilitychange", () => {
    if (document.hidden) {
      playAttempt++;
      track.pause();
    } else if (scene) {
      playMusic();
    }

    mix();
  });

  window.addEventListener("pagehide", stop);

  return { unlock, enter, stop };
})();

const $ = (id) => document.getElementById(id);

const ui = {
  menu: $("menu"),
  game: $("game"),
  title: $("scene-title"),
  narration: $("narration"),
  choices: $("choices"),
  label: $("scene-label"),
  heading: $("choice-heading"),
  start: $("start"),
  restart: $("restart"),
  leave: $("leave"),
  recover: $("recover"),
  feedback: $("feedback"),
  message: $("message"),
};

// Keep using the folder containing your existing scene images.
const IMAGE_ROOT = "/static/flannan-scene-pack/assets/scenes/";

// These mappings only preload artwork. Python validates story choices.
const NEXT_SCENES = {
  missing_report: ["case_report", "captain_warning", "crossing"],
  case_report: ["crossing"],
  captain_warning: ["crossing"],
  crossing: ["radio_identity", "lighthouse_exterior"],
  radio_identity: ["lighthouse_exterior"],
  lighthouse_exterior: ["entry_hall", "upper_window", "radio_warning"],
  upper_window: ["entry_hall"],
  radio_warning: ["entry_hall"],
  entry_hall: ["keeper_notebook", "west_landing", "staircase"],
  keeper_notebook: ["west_landing", "staircase"],
  west_landing: ["staircase", "captain_call"],
  captain_call: ["ending_departure", "staircase"],
  staircase: ["lantern_room", "door_voice"],
  door_voice: ["lantern_room"],
  lantern_room: ["ending_beacon", "ending_dark", "ending_departure"],
  ending_departure: [],
  ending_dark: [],
  ending_beacon: [],
};

// Create artwork layers without requiring changes to your HTML.
const stage = document.createElement("div");
stage.className = "scene-stage";
stage.setAttribute("aria-hidden", "true");

const layers = [0, 1].map(() => {
  const layer = document.createElement("div");
  layer.className = "scene-image";
  stage.append(layer);
  return layer;
});

const shade = document.createElement("div");
shade.className = "scene-shade";
stage.append(shade);
document.body.prepend(stage);

const artStatus = document.createElement("p");
artStatus.className = "art-status";
artStatus.setAttribute("role", "status");
artStatus.hidden = true;
ui.game.prepend(artStatus);

// Allow players to inspect artwork without losing story progress.
const viewButton = document.createElement("button");
viewButton.type = "button";
viewButton.className = "text-button view-scene";
viewButton.textContent = "View artwork";
viewButton.setAttribute("aria-pressed", "false");
ui.leave.before(viewButton);

viewButton.addEventListener("click", () => {
  setArtworkOnly(
    !document.body.classList.contains("artwork-only")
  );
});

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape") {
    setArtworkOnly(false);
  }
});

function setArtworkOnly(enabled) {
  document.body.classList.toggle("artwork-only", enabled);
  viewButton.setAttribute("aria-pressed", String(enabled));

  viewButton.textContent = enabled
    ? "Return to story"
    : "View artwork";

  const panel = document.querySelector(".play-layout");
  panel.inert = enabled;

  if (enabled) {
    panel.setAttribute("aria-hidden", "true");
  } else {
    panel.removeAttribute("aria-hidden");
  }
}

let currentScene = null;
let busy = false;
let needsRecovery = false;
let artworkGeneration = 0;
let activeLayer = -1;
let displayedScene = null;

const imageCache = new Map();

function imageUrl(sceneId) {
  if (!Object.hasOwn(NEXT_SCENES, sceneId)) {
    throw new Error("No artwork registered for this scene.");
  }

  return `${IMAGE_ROOT}${sceneId}.png`;
}

function loadImage(sceneId) {
  if (imageCache.has(sceneId)) {
    return imageCache.get(sceneId);
  }

  const image = new Image();
  image.decoding = "async";

  const promise = new Promise((resolve, reject) => {
    const timer = setTimeout(
      () => finish(new Error("Image load timed out.")),
      12000
    );

    function finish(error) {
      clearTimeout(timer);
      image.onload = null;
      image.onerror = null;

      if (error) {
        reject(error);
      } else {
        resolve(image);
      }
    }

    image.onload = () => finish();

    image.onerror = () => {
      finish(new Error("Scene image could not be loaded."));
    };

    image.src = imageUrl(sceneId);
  });

  imageCache.set(sceneId, promise);

  // Keep a small working set instead of retaining every decoded PNG.
  while (imageCache.size > 6) {
    imageCache.delete(imageCache.keys().next().value);
  }

  promise.catch(() => {
    if (imageCache.get(sceneId) === promise) {
      imageCache.delete(sceneId);
    }
  });

  return promise;
}

function preloadNext(sceneId) {
  for (const next of NEXT_SCENES[sceneId] || []) {
    loadImage(next).catch(() => {});
  }
}

function clearArtwork() {
  // Late image requests must not reappear after leaving the game.
  artworkGeneration += 1;

  for (const layer of layers) {
    layer.classList.remove("is-visible");
    layer.style.backgroundImage = "none";
  }

  activeLayer = -1;
  displayedScene = null;
  artStatus.hidden = true;
}

async function showArtwork(sceneId) {
  const generation = ++artworkGeneration;

  if (displayedScene === sceneId) return;

  artStatus.textContent = "Loading scene artwork…";
  artStatus.hidden = false;

  try {
    const image = await loadImage(sceneId);

    if (
      generation !== artworkGeneration ||
      !currentScene
    ) {
      return;
    }

    const nextIndex = activeLayer === 0 ? 1 : 0;
    const next = layers[nextIndex];

    // Prepare the spare image layer, then fade it over the current one.
    next.style.transition = "none";
    next.classList.remove("is-visible");
    next.style.backgroundImage = `url("${image.src}")`;
    next.style.zIndex = "2";

    if (activeLayer >= 0) {
      layers[activeLayer].style.zIndex = "1";
    }

    void next.offsetWidth;
    next.style.transition = "";
    next.classList.add("is-visible");

    const previous = activeLayer;
    activeLayer = nextIndex;
    displayedScene = sceneId;
    artStatus.hidden = true;

    setTimeout(() => {
      if (
        generation === artworkGeneration &&
        previous >= 0
      ) {
        layers[previous].classList.remove("is-visible");
      }
    }, 650);

    preloadNext(sceneId);
  } catch (error) {
    if (
      generation !== artworkGeneration ||
      !currentScene
    ) {
      return;
    }

    for (const layer of layers) {
      layer.classList.remove("is-visible");
    }

    activeLayer = -1;
    displayedScene = null;

    artStatus.textContent =
      `Artwork unavailable: ${sceneId}.png. ` +
      "Story controls still work. Use Refresh current scene to retry.";

    showFeedback(
      "Check that the scene PNG is inside " +
      "web\\flannan-scene-pack\\assets\\scenes."
    );
  }
}

// AI credentials remain on the server, never in browser requests.
async function api(path, method = "GET", data) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 15000);

  try {
    const response = await fetch(path, {
      method,
      credentials: "same-origin",
      cache: "no-store",
      headers: {
        "X-Flannan-Client": "browser",
        ...(data === undefined
          ? {}
          : { "Content-Type": "application/json" }),
      },
      ...(data === undefined
        ? {}
        : { body: JSON.stringify(data) }),
      signal: controller.signal,
    });

    const result = await response.json();

    if (!response.ok) {
      const error = new Error(
        typeof result.detail === "string"
          ? result.detail
          : "The request could not be completed."
      );

      error.status = response.status;
      throw error;
    }

    return result;
  } finally {
    clearTimeout(timer);
  }
}

function updateControls() {
  for (
    const button of document.querySelectorAll(
      "button:not([data-audio-control])"
    )
  ) {
    button.disabled = busy;
  }

  if (needsRecovery) {
    for (const button of [
      ui.start,
      ui.restart,
      ...ui.choices.querySelectorAll("button"),
    ]) {
      button.disabled = true;
    }
  }

  ui.game.setAttribute("aria-busy", String(busy));
}

function setBusy(value) {
  busy = value;
  updateControls();
}

function showFeedback(message) {
  ui.message.textContent = message;
  ui.feedback.hidden = false;
}

function hideFeedback() {
  ui.feedback.hidden = true;
  ui.message.textContent = "";
}

function showMenu() {
  soundEngine.stop();
  currentScene = null;
  needsRecovery = false;

  clearArtwork();
  setArtworkOnly(false);

  document.body.classList.remove("in-game");
  ui.game.hidden = true;
  ui.menu.hidden = false;

  delete ui.game.dataset.sound;
  delete ui.game.dataset.effect;
  delete ui.game.dataset.delivery;
}

function renderScene(scene) {
  currentScene = scene;
  needsRecovery = false;

  setArtworkOnly(false);
  document.body.classList.add("in-game");

  ui.menu.hidden = true;
  ui.game.hidden = false;
  ui.title.textContent = scene.title;

  ui.label.textContent = scene.ending
    ? "END OF PLAYTHROUGH"
    : "THE INVESTIGATION";

  ui.heading.textContent = scene.ending
    ? "YOUR STORY ENDS HERE"
    : "WHAT WILL YOU DO?";

  ui.narration.replaceChildren();

  // Render narration as text, never executable HTML.
  for (
    const paragraph of scene.narration.split(/\n\s*\n/)
  ) {
    if (!paragraph.trim()) continue;

    const p = document.createElement("p");
    p.textContent = paragraph.trim();
    ui.narration.append(p);
  }

  ui.choices.replaceChildren();

  scene.choices.forEach((choice, index) => {
    const button = document.createElement("button");
    button.className = "choice";
    button.type = "button";

    const number = document.createElement("span");
    number.className = "choice-number";
    number.setAttribute("aria-hidden", "true");
    number.textContent = String(index + 1).padStart(2, "0");

    const label = document.createElement("span");
    label.textContent = choice.label;

    button.append(number, label);

    button.addEventListener("click", () => {
      submitChoice(choice.keyword);
    });

    ui.choices.append(button);
  });

  ui.restart.hidden = !scene.ending;

  // Keep presentation cues available without showing diagnostic text.
  for (const cue of ["sound", "effect", "delivery"]) {
    ui.game.dataset[cue] = scene.cues?.[cue] || "";
  }

  document.querySelector(".story-card").scrollTop = 0;
  ui.title.focus({ preventScroll: true });
  window.scrollTo({ top: 0, behavior: "instant" });

  updateControls();

  // Media loading never blocks narration or player choices.
  soundEngine.enter(scene);
  void showArtwork(scene.scene_id);
}

async function restoreState() {
  try {
    renderScene(await api("/api/game"));
  } catch (error) {
    if (error.status === 404) {
      showMenu();
    } else {
      throw error;
    }
  }
}

async function recoverGame() {
  if (busy) return;

  setBusy(true);
  hideFeedback();

  try {
    await restoreState();
  } catch (error) {
    needsRecovery = true;

    showFeedback(
      "Cannot reach the game server. Check that Uvicorn is running, " +
      "then refresh the current scene."
    );
  } finally {
    setBusy(false);
  }
}

async function mutate(path, method, data) {
  if (busy) return;

  setBusy(true);
  hideFeedback();

  try {
    const result = await api(path, method, data);

    if (method === "DELETE") {
      showMenu();
    } else {
      renderScene(result);
    }
  } catch (error) {
    // A lost response may still have applied a choice. Do not resend it.
    needsRecovery = true;

    try {
      await restoreState();

      showFeedback(
        "The request was interrupted or rejected. " +
        "The current server state has been restored."
      );
    } catch (recoveryError) {
      showFeedback(
        "Connection lost. Refresh the current scene before choosing again."
      );
    }
  } finally {
    setBusy(false);
  }
}

function submitChoice(keyword) {
  if (!currentScene || busy || needsRecovery) return;

  soundEngine.unlock();

  void mutate("/api/game/choice", "POST", {
    keyword,
    revision: currentScene.revision,
  });
}

ui.start.addEventListener("click", () => {
  soundEngine.unlock();
  void mutate("/api/game", "POST");
});

ui.restart.addEventListener("click", () => {
  soundEngine.unlock();
  void mutate("/api/game", "POST");
});

ui.leave.addEventListener("click", () => {
  void mutate("/api/game", "DELETE");
});

ui.recover.addEventListener("click", recoverGame);

// Preload only the opening artwork while the player reads the menu.
loadImage("missing_report").catch(() => {});
void recoverGame();