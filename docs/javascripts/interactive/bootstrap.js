import { ActivityEngine } from "./activity-engine.js";
import { renderAcknowledgement } from "./activities/acknowledgement.js";
import { BrowserProgressStore } from "./browser-progress-store.js";


const scriptUrl = new URL(import.meta.url);
const manifestUrl = new URL("../../assets/generated/activities.json", scriptUrl);
const store = new BrowserProgressStore();
const engine = new ActivityEngine({
  store,
  renderers: new Map([["acknowledgement", renderAcknowledgement]]),
});

let manifestPromise;


function loadManifest() {
  if (!manifestPromise) {
    manifestPromise = fetch(manifestUrl).then((response) => {
      if (!response.ok) {
        throw new Error(`Nie udało się pobrać manifestu (${response.status}).`);
      }
      return response.json();
    });
  }
  return manifestPromise;
}


async function renderActivities() {
  if (!document.querySelector("[data-activity-slot]")) {
    return;
  }

  try {
    const manifest = await loadManifest();
    const activities = Array.isArray(manifest.activities)
      ? manifest.activities
      : [];
    await engine.render(document, activities);
  } catch (error) {
    console.warn("Nie udało się zainicjalizować aktywności.", error);
  }
}


if (typeof document$ !== "undefined") {
  document$.subscribe(renderActivities);
} else if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", renderActivities, { once: true });
} else {
  renderActivities();
}
