import {
  createProgressRail,
  deriveCompletionProgress,
  insertProgressRail,
  removeProgressRail,
  updateProgressRail,
} from "./progress-rail.js";


const PRIMARY_SIDEBAR_SELECTOR = ".md-sidebar--primary";
const HREF_SELECTOR = "[href]";
const MARKER_SELECTOR = "[data-interactive-page-progress]";


function requireDependencies({ document, completionSource, siteBaseUrl }) {
  if (
    !document
    || typeof document.createElement !== "function"
    || typeof document.querySelectorAll !== "function"
  ) {
    throw new TypeError("Wskaźniki stron wymagają obiektu document.");
  }
  if (
    !completionSource
    || typeof completionSource.getActivityCompletion !== "function"
    || typeof completionSource.subscribeActivityCompletion !== "function"
  ) {
    throw new TypeError(
      "Wskaźniki stron wymagają źródła statusów aktywności.",
    );
  }

  try {
    return new URL(siteBaseUrl, document.baseURI);
  } catch (error) {
    if (error instanceof TypeError) {
      throw new TypeError("Wskaźniki stron wymagają poprawnego URL serwisu.");
    }
    throw error;
  }
}


function nonEmptyString(value) {
  return typeof value === "string" && value.trim() !== "";
}


function attributeValue(element, attribute) {
  if (typeof element?.getAttribute !== "function") {
    return null;
  }
  const value = element.getAttribute(attribute);
  return typeof value === "string" ? value : null;
}


function hasClass(element, className) {
  const classes = typeof element?.className === "string"
    ? element.className
    : attributeValue(element, "class") ?? "";
  return classes.split(/\s+/).includes(className);
}


function isAnchor(element) {
  return String(element?.tagName).toLowerCase() === "a";
}


function belongsToLocalToc(link, sidebar) {
  let element = link.parentNode;
  while (element && element !== sidebar) {
    if (
      hasClass(element, "md-nav--secondary")
      || attributeValue(element, "data-md-component") === "toc"
    ) {
      return true;
    }
    element = element.parentNode;
  }
  return false;
}


function normalizedUrl(value, baseUrl) {
  try {
    const url = new URL(value, baseUrl);
    url.hash = "";
    url.search = "";
    return url;
  } catch (error) {
    if (error instanceof TypeError) {
      return null;
    }
    throw error;
  }
}


export function pageUrlKey(value, baseUrl) {
  const url = normalizedUrl(value, baseUrl);
  return url ? `${url.origin}${url.pathname}` : null;
}


function isWithinSite(url, siteBaseUrl) {
  if (url.origin !== siteBaseUrl.origin) {
    return false;
  }

  const basePath = siteBaseUrl.pathname.endsWith("/")
    ? siteBaseUrl.pathname
    : `${siteBaseUrl.pathname}/`;
  return url.pathname === siteBaseUrl.pathname
    || url.pathname.startsWith(basePath);
}


function collectManifestIndex(manifest, siteBaseUrl) {
  const activities = Array.isArray(manifest?.activities)
    ? manifest.activities
    : [];
  const activitiesByPageKey = new Map();
  const pageKeyByActivityId = new Map();
  const trackedActivityIds = [];
  const trackedActivityIdSet = new Set();
  const invalidPageUrlActivityIds = [];

  for (const activity of activities) {
    if (!nonEmptyString(activity?.activity_id)) {
      continue;
    }

    const activityId = activity.activity_id;
    if (!trackedActivityIdSet.has(activityId)) {
      trackedActivityIdSet.add(activityId);
      trackedActivityIds.push(activityId);
    }

    if (pageKeyByActivityId.has(activityId)) {
      continue;
    }

    const pageUrl = typeof activity.page_url === "string"
      ? normalizedUrl(activity.page_url, siteBaseUrl)
      : null;
    if (!pageUrl || !isWithinSite(pageUrl, siteBaseUrl)) {
      invalidPageUrlActivityIds.push(activityId);
      continue;
    }
    const pageKey = pageUrlKey(pageUrl, siteBaseUrl);

    const pageActivityIds = activitiesByPageKey.get(pageKey) ?? [];
    pageActivityIds.push(activityId);
    activitiesByPageKey.set(pageKey, pageActivityIds);
    pageKeyByActivityId.set(activityId, pageKey);
  }

  return {
    activitiesByPageKey,
    invalidPageUrlActivityIds,
    pageKeyByActivityId,
    trackedActivityIds,
  };
}


/**
 * Dekoruje wyłącznie rzeczywiste linki stron w głównej nawigacji.
 * Nie modyfikuje href, klas ani obramowania linku Material.
 */
export function createPageProgressController({
  document,
  manifest,
  completionSource,
  siteBaseUrl,
}) {
  const normalizedSiteBaseUrl = requireDependencies({
    document,
    completionSource,
    siteBaseUrl,
  });
  normalizedSiteBaseUrl.hash = "";
  normalizedSiteBaseUrl.search = "";

  const {
    activitiesByPageKey,
    invalidPageUrlActivityIds,
    pageKeyByActivityId,
    trackedActivityIds,
  } = collectManifestIndex(manifest, normalizedSiteBaseUrl);
  let markersByPageKey = new Map();
  let destroyed = false;
  let invalidManifestWarningEmitted = false;

  function pageIndexAvailable() {
    if (invalidPageUrlActivityIds.length === 0) {
      return true;
    }
    if (!invalidManifestWarningEmitted) {
      invalidManifestWarningEmitted = true;
      console.warn(
        "Nie można wyświetlić postępu stron: manifest nie zawiera "
          + "poprawnego page_url dla aktywności: "
          + invalidPageUrlActivityIds.join(", ")
          + ". Po zmianie hooka zrestartuj mkdocs serve.",
      );
    }
    return false;
  }

  function completionModelAvailable() {
    return trackedActivityIds.every((activityId) => (
      typeof completionSource.getActivityCompletion(activityId) === "boolean"
    ));
  }

  function removeCurrentMarkers() {
    for (const marker of document.querySelectorAll(MARKER_SELECTOR)) {
      removeProgressRail(marker);
    }
    markersByPageKey = new Map();
  }

  function progressForPage(pageKey) {
    return deriveCompletionProgress(
      activitiesByPageKey.get(pageKey) ?? [],
      (activityId) => completionSource.getActivityCompletion(activityId),
    );
  }

  function pageKeyForLink(link) {
    const href = attributeValue(link, "href");
    if (href === null) {
      return null;
    }

    let resolved;
    try {
      resolved = new URL(href, document.baseURI);
    } catch (error) {
      if (error instanceof TypeError) {
        return null;
      }
      throw error;
    }

    if (resolved.hash || !isWithinSite(resolved, normalizedSiteBaseUrl)) {
      return null;
    }
    return pageUrlKey(resolved, normalizedSiteBaseUrl);
  }

  function pageLinks() {
    const links = [];
    for (const sidebar of document.querySelectorAll(PRIMARY_SIDEBAR_SELECTOR)) {
      if (
        attributeValue(sidebar, "data-md-type") !== null
        && attributeValue(sidebar, "data-md-type") !== "navigation"
      ) {
        continue;
      }
      if (typeof sidebar?.querySelectorAll !== "function") {
        continue;
      }

      for (const link of sidebar.querySelectorAll(HREF_SELECTOR)) {
        if (
          !isAnchor(link)
          || !hasClass(link, "md-nav__link")
          || belongsToLocalToc(link, sidebar)
        ) {
          continue;
        }
        const pageKey = pageKeyForLink(link);
        if (pageKey) {
          links.push({ link, pageKey });
        }
      }
    }
    return links;
  }

  function decorateNavigation() {
    if (destroyed) {
      return 0;
    }

    removeCurrentMarkers();
    if (!pageIndexAvailable() || !completionModelAvailable()) {
      return 0;
    }

    let markerCount = 0;
    for (const { link, pageKey } of pageLinks()) {
      const progress = progressForPage(pageKey);
      if (!progress) {
        removeCurrentMarkers();
        return 0;
      }

      const marker = createProgressRail({
        document,
        kind: "page",
        progress,
      });
      if (!insertProgressRail(link, marker)) {
        continue;
      }

      const markers = markersByPageKey.get(pageKey) ?? [];
      markers.push(marker);
      markersByPageKey.set(pageKey, markers);
      markerCount += 1;
    }
    return markerCount;
  }

  function updatePagesForActivityIds(activityIds) {
    if (
      destroyed
      || !pageIndexAvailable()
      || !completionModelAvailable()
    ) {
      removeCurrentMarkers();
      return;
    }

    const pageKeys = new Set();
    for (const activityId of new Set(
      Array.isArray(activityIds) ? activityIds : [],
    )) {
      const pageKey = pageKeyByActivityId.get(activityId);
      if (pageKey && markersByPageKey.has(pageKey)) {
        pageKeys.add(pageKey);
      }
    }

    for (const pageKey of pageKeys) {
      const progress = progressForPage(pageKey);
      if (!progress) {
        removeCurrentMarkers();
        return;
      }
      for (const marker of markersByPageKey.get(pageKey) ?? []) {
        updateProgressRail(marker, { kind: "page", progress });
      }
    }
  }

  const unsubscribe = completionSource.subscribeActivityCompletion((event) => {
    if (Array.isArray(event?.activityIds)) {
      updatePagesForActivityIds(event.activityIds);
    }
  });

  function destroy() {
    if (destroyed) {
      return;
    }
    destroyed = true;
    unsubscribe();
    removeCurrentMarkers();
  }

  return {
    decorateNavigation,
    destroy,
  };
}
