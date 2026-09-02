const KINDS = Object.freeze({
  page: Object.freeze({
    attribute: "data-interactive-page-progress",
    emptyDescription: "Do tej strony nie przypisano ćwiczeń.",
    progressDescription(completed, total) {
      return `Ćwiczenia na tej stronie: ukończono ${completed} z ${total}.`;
    },
  }),
  section: Object.freeze({
    attribute: "data-interactive-section-progress",
    emptyDescription: "Do tej sekcji nie przypisano ćwiczeń.",
    progressDescription(completed, total) {
      return `Ćwiczenia w tej sekcji: ukończono ${completed} z ${total}.`;
    },
  }),
});


function requireKind(kind) {
  const definition = KINDS[kind];
  if (!definition) {
    throw new TypeError(`Nieznany rodzaj wskaźnika postępu: ${kind}.`);
  }
  return definition;
}


function hasClass(element, className) {
  const classes = typeof element?.className === "string"
    ? element.className
    : element?.getAttribute?.("class") ?? "";
  return classes.split(/\s+/).includes(className);
}


function findEllipsis(link) {
  if (typeof link?.querySelector === "function") {
    const ellipsis = link.querySelector(".md-ellipsis");
    if (ellipsis) {
      return ellipsis;
    }
  }
  return [...(link?.children ?? [])].find(
    (child) => hasClass(child, "md-ellipsis"),
  ) ?? null;
}


function descriptionFor(kind, progress) {
  const definition = requireKind(kind);
  return progress.total === 0
    ? definition.emptyDescription
    : definition.progressDescription(progress.completed, progress.total);
}


/**
 * Wylicza stan agregatu bez tworzenia dodatkowego cache'u ukończeń.
 * `null` oznacza, że współdzielony model postępu nie jest dostępny.
 */
export function deriveCompletionProgress(
  activityIds,
  getActivityCompletion,
) {
  if (typeof getActivityCompletion !== "function") {
    throw new TypeError("Stan postępu wymaga funkcji odczytu ukończenia.");
  }

  const uniqueActivityIds = [...new Set(
    Array.isArray(activityIds) ? activityIds : [],
  )];
  const total = uniqueActivityIds.length;
  if (total === 0) {
    return { completed: 0, state: "none", total: 0 };
  }

  let completed = 0;
  for (const activityId of uniqueActivityIds) {
    const activityCompleted = getActivityCompletion(activityId);
    if (typeof activityCompleted !== "boolean") {
      return null;
    }
    if (activityCompleted) {
      completed += 1;
    }
  }

  let state = "partial";
  if (completed === 0) {
    state = "none_completed";
  } else if (completed === total) {
    state = "completed";
  }

  return { completed, state, total };
}


export function updateProgressRail(marker, { kind, progress }) {
  const definition = requireKind(kind);
  if (!marker || !progress) {
    throw new TypeError("Aktualizacja wskaźnika wymaga elementu i stanu.");
  }

  const [visual, accessibleDescription] = marker.children ?? [];
  if (!visual || !accessibleDescription) {
    throw new TypeError("Wskaźnik postępu ma niepoprawną strukturę DOM.");
  }

  marker.className = [
    "interactive-progress-rail",
    `interactive-progress-rail--${kind}`,
    `interactive-progress-rail--${progress.state}`,
  ].join(" ");
  marker.setAttribute(definition.attribute, "");
  marker.setAttribute("data-state", progress.state);

  const description = descriptionFor(kind, progress);
  marker.setAttribute("title", description);
  accessibleDescription.textContent = description;

  return marker;
}


export function createProgressRail({ document, kind, progress }) {
  if (!document || typeof document.createElement !== "function") {
    throw new TypeError("Wskaźnik postępu wymaga obiektu document.");
  }
  requireKind(kind);

  const marker = document.createElement("span");

  const visual = document.createElement("span");
  visual.className = "interactive-progress-rail__visual";
  visual.setAttribute("aria-hidden", "true");

  const accessibleDescription = document.createElement("span");
  accessibleDescription.className = "interactive-activity__visually-hidden";

  marker.append(visual, accessibleDescription);
  return updateProgressRail(marker, { kind, progress });
}


/**
 * Marker pozostaje po etykiecie w kolejności DOM. Własna reguła CSS raila
 * przenosi go wizualnie do pierwszej kolumny bez modyfikowania samego linku.
 */
export function insertProgressRail(link, marker) {
  if (!link || !marker) {
    return false;
  }

  const ellipsis = findEllipsis(link);
  if (ellipsis && typeof ellipsis.after === "function") {
    ellipsis.after(marker);
    return true;
  }
  if (
    ellipsis?.parentNode
    && typeof ellipsis.parentNode.insertBefore === "function"
  ) {
    ellipsis.parentNode.insertBefore(marker, ellipsis.nextSibling ?? null);
    return true;
  }
  if (typeof link.append === "function") {
    link.append(marker);
    return true;
  }
  if (typeof link.appendChild === "function") {
    link.appendChild(marker);
    return true;
  }
  return false;
}


export function removeProgressRail(marker) {
  if (typeof marker?.remove === "function") {
    marker.remove();
    return;
  }
  if (typeof marker?.parentNode?.removeChild === "function") {
    marker.parentNode.removeChild(marker);
  }
}
