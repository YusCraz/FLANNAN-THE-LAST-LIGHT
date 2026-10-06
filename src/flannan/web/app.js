"use strict";

const menu = document.querySelector("#menu");
const game = document.querySelector("#game");
const title = document.querySelector("#scene-title");
const narration = document.querySelector("#narration");
const choices = document.querySelector("#choices");
const sceneLabel = document.querySelector("#scene-label");
const choiceHeading = document.querySelector("#choice-heading");

const startButton = document.querySelector("#start");
const restartButton = document.querySelector("#restart");
const leaveButton = document.querySelector("#leave");
const recoverButton = document.querySelector("#recover");
const feedback = document.querySelector("#feedback");
const message = document.querySelector("#message");

let currentScene = null;
let busy = false;


// Send requests to our own Python server, never directly to Hugging Face.
async function api(path, method = "GET", body = undefined) {
  const headers = {
    "X-Flannan-Client": "browser",
  };

  if (body !== undefined) {
    headers["Content-Type"] = "application/json";
  }

  const response = await fetch(path, {
    method,
    headers,
    credentials: "same-origin",
    cache: "no-store",
    body: body === undefined ? undefined : JSON.stringify(body),
  });

  const data = await response.json();

  if (!response.ok) {
    const error = new Error(
      typeof data.detail === "string"
        ? data.detail
        : "The request could not be completed."
    );

    error.status = response.status;
    throw error;
  }

  return data;
}


// Prevent repeated clicks while a browser request is in progress.
function setBusy(value) {
  busy = value;

  document.querySelectorAll("button").forEach((button) => {
    button.disabled = value;
  });
}


function clearFeedback() {
  feedback.hidden = true;
  message.textContent = "";
}


function showError(error) {
  message.textContent =
    error instanceof TypeError
      ? "Cannot reach the game server. Check that it is running, then refresh the current scene."
      : error.message;

  feedback.hidden = false;
}


function showMenu() {
  currentScene = null;
  menu.hidden = false;
  game.hidden = true;
  document.title = "FLANNAN — The Last Light";
}


// Render text safely without inserting model output as HTML.
function renderScene(scene, focus = true) {
  currentScene = scene;
  menu.hidden = true;
  game.hidden = false;

  title.textContent = scene.title;
  document.title = `${scene.title} — FLANNAN`;
  sceneLabel.textContent = scene.ending
    ? "THE END"
    : "THE INVESTIGATION";

  narration.replaceChildren();

  for (const paragraph of scene.narration.split(/\n\s*\n/)) {
    const element = document.createElement("p");
    element.textContent = paragraph;
    narration.append(element);
  }

  choices.replaceChildren();

  scene.choices.forEach((choice, index) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "choice";

    const number = document.createElement("span");
    number.className = "choice-number";
    number.textContent = String(index + 1).padStart(2, "0");
    number.setAttribute("aria-hidden", "true");

    const label = document.createElement("span");
    label.textContent = choice.label;

    button.append(number, label);
    button.addEventListener("click", () => submitChoice(choice.keyword));
    choices.append(button);
  });

  choiceHeading.hidden = scene.ending;
  restartButton.hidden = !scene.ending;

  // Retain approved cues for the upcoming Rive/audio integration.
  // They deliberately produce no fake sound or animation yet.
  game.dataset.scene = scene.scene_id;
  game.dataset.delivery = scene.cues.delivery;
  game.dataset.sound = scene.cues.sound;
  game.dataset.effect = scene.cues.effect;

  if (focus) {
    title.focus({ preventScroll: true });
    window.scrollTo({ top: 0, behavior: "instant" });
  }
}


// Recover authoritative state rather than blindly resubmitting a choice.
async function restoreGame(focus = false) {
  try {
    const scene = await api("/api/game");
    renderScene(scene, focus);
  } catch (error) {
    if (error.status === 404) {
      showMenu();
      return;
    }

    throw error;
  }
}


async function startGame() {
  if (busy) return;

  setBusy(true);
  clearFeedback();

  try {
    const scene = await api("/api/game", "POST");
    renderScene(scene);
  } catch (error) {
    showError(error);
  } finally {
    setBusy(false);
  }
}


async function submitChoice(keyword) {
  if (busy || currentScene === null) return;

  setBusy(true);
  clearFeedback();

  try {
    const scene = await api("/api/game/choice", "POST", {
      keyword,
      revision: currentScene.revision,
    });

    renderScene(scene);
  } catch (error) {
    // The server may have advanced even if the response was interrupted.
    // Reload state before allowing another action.
    try {
      await restoreGame();
    } catch {
      // Preserve the original error; the recovery button remains available.
    }

    showError(error);
  } finally {
    setBusy(false);
  }
}


async function leaveGame() {
  if (busy) return;

  setBusy(true);
  clearFeedback();

  try {
    await api("/api/game", "DELETE");
    showMenu();
  } catch (error) {
    showError(error);
  } finally {
    setBusy(false);
  }
}


async function recoverGame() {
  if (busy) return;

  setBusy(true);
  clearFeedback();

  try {
    await restoreGame(true);
  } catch (error) {
    showError(error);
  } finally {
    setBusy(false);
  }
}


startButton.addEventListener("click", startGame);
restartButton.addEventListener("click", startGame);
leaveButton.addEventListener("click", leaveGame);
recoverButton.addEventListener("click", recoverGame);

// Restore the session on refresh, if the Python process still holds it.
recoverGame();