import {
  createProgressRail,
  deriveCompletionProgress,
  insertProgressRail,
  removeProgressRail,
  updateProgressRail,
} from "./progress-rail.js";


const SECTION_SELECTOR = "[data-activity-section=\"true\"]";
const SLOT_SELECTOR = "[data-activity-slot]";
const TOC_SELECTOR = "[data-md-component=\"toc\"]";
const HREF_SELECTOR = "[href]";
const MARKER_SELECTOR = "[data-interactive-section-progress]";


function requireDependencies({ document, completionSource }) {
  if (
    !document
    || typeof document.createElement !== "function"
    || typeof document.querySelectorAll !== "function"
  ) {
    throw new TypeError("Wskaźniki sekcji wymagają obiektu document.");
  }
  if (
    !completionSource
    || typeof completionSource.getActivityCompletion !== "function"
    || typeof completionSource.subscribeActivityCompletion !== "function"
  ) {
    throw new TypeError(
      "Wskaźniki sekcji wymagają źródła statusów aktywności.",
    );
  }
}


function nonEmptyString(value) {
  return typeof value === "string" && value.trim() !== "";
}


function collectManifestIndex(manifest) {
  const activities = Array.isArray(manifest?.activities)
    ? manifest.activities
    : [];
  const activitiesBySlotAndSection = new Map();
  const bindingByActivityId = new Map();
  const trackedActivityIds = [];
  const trackedActivityIdSet = new Set();

  for (const activity of activities) {
    if (!nonEmptyString(activity?.activity_id)) {
      continue;
    }

    const activityId = activity.activity_id;
    if (!trackedActivityIdSet.has(activityId)) {
      trackedActivityIdSet.add(activityId);
      trackedActivityIds.push(activityId);
    }

    if (
      !nonEmptyString(activity.slot_id)
      || !nonEmptyString(activity.section_id)
      || bindingByActivityId.has(activityId)
    ) {
      continue;
    }

    const slotId = activity.slot_id;
    const sectionId = activity.section_id;
    const sections = activitiesBySlotAndSection.get(slotId) ?? new Map();
    const sectionActivityIds = sections.get(sectionId) ?? [];
    sectionActivityIds.push(activityId);
    sections.set(sectionId, sectionActivityIds);
    activitiesBySlotAndSection.set(slotId, sections);
    bindingByActivityId.set(activityId, { sectionId, slotId });
  }

  return {
    activitiesBySlotAndSection,
    bindingByActivityId,
    trackedActivityIds,
  };
}


export function deriveSectionProgress(
  activityIds,
  getActivityCompletion,
) {
  return deriveCompletionProgress(activityIds, getActivityCompletion);
}


export function sectionIdFromHref(href, baseURI) {
  if (!nonEmptyString(href) || !nonEmptyString(baseURI)) {
    return null;
  }

  try {
    const url = new URL(href, baseURI);
    if (!url.hash) {
      return null;
    }
    return decodeURIComponent(url.hash.slice(1));
  } catch (error) {
    if (error instanceof TypeError || error instanceof URIError) {
      return null;
    }
    throw error;
  }
}


function elementId(element) {
  if (nonEmptyString(element?.id)) {
    return element.id;
  }
  if (typeof element?.getAttribute === "function") {
    const id = element.getAttribute("id");
    return nonEmptyString(id) ? id : null;
  }
  return null;
}


function attributeValue(element, attribute) {
  if (typeof element?.getAttribute !== "function") {
    return null;
  }
  const value = element.getAttribute(attribute);
  return typeof value === "string" ? value : null;
}


export function createSectionProgressController({
  document,
  manifest,
  completionSource,
}) {
  requireDependencies({ document, completionSource });
  const {
    activitiesBySlotAndSection,
    bindingByActivityId,
    trackedActivityIds,
  } = collectManifestIndex(manifest);
  let currentSlotId = null;
  let currentActivityIdsBySection = new Map();
  let markersBySection = new Map();
  let destroyed = false;

  function completionModelAvailable() {
    return trackedActivityIds.every((activityId) => (
      typeof completionSource.getActivityCompletion(activityId) === "boolean"
    ));
  }

  function removeCurrentMarkers() {
    const markers = typeof document.querySelectorAll === "function"
      ? document.querySelectorAll(MARKER_SELECTOR)
      : [];
    for (const marker of markers) {
      removeProgressRail(marker);
    }
    markersBySection = new Map();
  }

  function currentSlot() {
    const slots = document.querySelectorAll(SLOT_SELECTOR);
    for (const slot of slots) {
      const slotId = attributeValue(slot, "data-activity-slot");
      if (nonEmptyString(slotId)) {
        return slotId;
      }
    }
    return null;
  }

  function markedSectionIds() {
    const sectionIds = new Set();
    for (const section of document.querySelectorAll(SECTION_SELECTOR)) {
      const sectionId = elementId(section);
      if (sectionId) {
        sectionIds.add(sectionId);
      }
    }
    return [...sectionIds];
  }

  function createCurrentSectionMap(sectionIds) {
    const activitiesBySection = currentSlotId === null
      ? new Map()
      : activitiesBySlotAndSection.get(currentSlotId) ?? new Map();
    return new Map(sectionIds.map((sectionId) => [
      sectionId,
      activitiesBySection.get(sectionId) ?? [],
    ]));
  }

  function progressForSection(sectionId) {
    return deriveSectionProgress(
      currentActivityIdsBySection.get(sectionId) ?? [],
      (activityId) => completionSource.getActivityCompletion(activityId),
    );
  }

  function linksBySection(sectionIds) {
    const expectedSectionIds = new Set(sectionIds);
    const result = new Map(sectionIds.map((sectionId) => [sectionId, new Set()]));

    for (const toc of document.querySelectorAll(TOC_SELECTOR)) {
      if (typeof toc?.querySelectorAll !== "function") {
        continue;
      }
      for (const link of toc.querySelectorAll(HREF_SELECTOR)) {
        if (String(link?.tagName).toLowerCase() !== "a") {
          continue;
        }
        const sectionId = sectionIdFromHref(
          attributeValue(link, "href"),
          document.baseURI,
        );
        if (sectionId && expectedSectionIds.has(sectionId)) {
          result.get(sectionId).add(link);
        }
      }
    }

    return result;
  }

  function decorateCurrentPage() {
    if (destroyed) {
      return 0;
    }

    removeCurrentMarkers();
    currentSlotId = null;
    currentActivityIdsBySection = new Map();

    const sectionIds = markedSectionIds();
    if (sectionIds.length === 0 || !completionModelAvailable()) {
      return 0;
    }

    currentSlotId = currentSlot();
    currentActivityIdsBySection = createCurrentSectionMap(sectionIds);
    const tocLinksBySection = linksBySection(sectionIds);
    let markerCount = 0;

    for (const sectionId of sectionIds) {
      const progress = progressForSection(sectionId);
      if (!progress) {
        removeCurrentMarkers();
        return 0;
      }

      const markers = [];
      for (const link of tocLinksBySection.get(sectionId) ?? []) {
        const marker = createProgressRail({
          document,
          kind: "section",
          progress,
        });
        if (!insertProgressRail(link, marker)) {
          continue;
        }
        markers.push(marker);
        markerCount += 1;
      }
      markersBySection.set(sectionId, markers);
    }

    return markerCount;
  }

  function updateSectionsForActivityIds(activityIds) {
    if (destroyed || !completionModelAvailable()) {
      removeCurrentMarkers();
      return;
    }

    const sectionIds = new Set();
    for (const activityId of new Set(activityIds)) {
      const binding = bindingByActivityId.get(activityId);
      if (
        binding
        && binding.slotId === currentSlotId
        && currentActivityIdsBySection.has(binding.sectionId)
      ) {
        sectionIds.add(binding.sectionId);
      }
    }

    for (const sectionId of sectionIds) {
      const progress = progressForSection(sectionId);
      if (!progress) {
        removeCurrentMarkers();
        return;
      }
      for (const marker of markersBySection.get(sectionId) ?? []) {
        updateProgressRail(marker, { kind: "section", progress });
      }
    }
  }

  const unsubscribe = completionSource.subscribeActivityCompletion((event) => {
    if (Array.isArray(event?.activityIds)) {
      updateSectionsForActivityIds(event.activityIds);
    }
  });

  function destroy() {
    if (destroyed) {
      return;
    }
    destroyed = true;
    unsubscribe();
    removeCurrentMarkers();
    currentActivityIdsBySection.clear();
  }

  return {
    decorateCurrentPage,
    destroy,
  };
}
