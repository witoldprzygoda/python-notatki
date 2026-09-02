import { ActivityEngine } from "./activity-engine.js";
import { renderAcknowledgement } from "./activities/acknowledgement.js";
import { createCodeRenderer } from "./activities/code.js";
import { renderSingleChoice } from "./activities/single-choice.js";
import { BrowserProgressStore } from "./browser-progress-store.js";
import { createGlobalProgressController } from "./global-progress.js";
import { NotifyingProgressStore } from "./notifying-progress-store.js";
import { createPageProgressController } from "./page-progress.js";
import { PyodideRuntime } from "./pyodide-runtime.js";
import { createSectionProgressController } from "./section-progress.js";


const scriptUrl = new URL(import.meta.url);
const siteBaseUrl = new URL("../../", scriptUrl);
const manifestUrl = new URL("assets/generated/activities.json", siteBaseUrl);
const store = new NotifyingProgressStore(new BrowserProgressStore());
const pyodideRuntime = new PyodideRuntime();
const engine = new ActivityEngine({
  store,
  renderers: new Map([
    ["acknowledgement", renderAcknowledgement],
    ["single_choice", renderSingleChoice],
    ["code", createCodeRenderer({ runtime: pyodideRuntime })],
  ]),
});

let manifestPromise;
let globalProgressController;
let pageProgressController;
let sectionProgressController;
let documentGeneration = 0;
let renderedDocument = false;


function loadManifest() {
  if (!manifestPromise) {
    manifestPromise = fetch(manifestUrl)
      .then((response) => {
        if (!response.ok) {
          throw new Error(`Nie udało się pobrać manifestu (${response.status}).`);
        }
        return response.json();
      })
      .catch((error) => {
        manifestPromise = undefined;
        throw error;
      });
  }
  return manifestPromise;
}


function getGlobalProgressController(manifest) {
  if (!globalProgressController) {
    globalProgressController = createGlobalProgressController({
      manifest,
      store,
    });
  }
  return globalProgressController;
}


function getSectionProgressController(manifest, globalProgress) {
  if (!sectionProgressController) {
    sectionProgressController = createSectionProgressController({
      document,
      manifest,
      completionSource: globalProgress,
    });
  }
  return sectionProgressController;
}


function getPageProgressController(manifest, globalProgress) {
  if (!pageProgressController) {
    pageProgressController = createPageProgressController({
      document,
      manifest,
      completionSource: globalProgress,
      siteBaseUrl,
    });
  }
  return pageProgressController;
}


async function renderInteractiveLayer() {
  const generation = ++documentGeneration;

  if (renderedDocument) {
    pyodideRuntime.reset();
  }
  renderedDocument = true;

  try {
    const manifest = await loadManifest();
    if (generation !== documentGeneration) {
      return;
    }

    const activities = Array.isArray(manifest.activities)
      ? manifest.activities
      : [];
    const globalProgress = getGlobalProgressController(manifest);

    try {
      await globalProgress.ready;
    } catch (error) {
      if (globalProgressController === globalProgress) {
        globalProgress.destroy();
        globalProgressController = undefined;
      }
      throw error;
    }

    if (generation !== documentGeneration) {
      return;
    }

    try {
      getPageProgressController(
        manifest,
        globalProgress,
      ).decorateNavigation();
    } catch (error) {
      console.warn("Nie udało się udekorować nawigacji stron.", error);
    }

    try {
      getSectionProgressController(
        manifest,
        globalProgress,
      ).decorateCurrentPage();
    } catch (error) {
      console.warn("Nie udało się udekorować lokalnego spisu treści.", error);
    }

    if (document.querySelector("[data-activity-slot]")) {
      await engine.render(document, activities);
    }
  } catch (error) {
    if (generation === documentGeneration) {
      console.warn("Nie udało się zainicjalizować warstwy interaktywnej.", error);
    }
  }
}


if (typeof document$ !== "undefined") {
  document$.subscribe(renderInteractiveLayer);
} else if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", renderInteractiveLayer, {
    once: true,
  });
} else {
  renderInteractiveLayer();
}
