export function createPageActivities(document) {
  const details = document.createElement("details");
  details.className = "interactive-activity-group";

  const summary = document.createElement("summary");
  summary.className = "interactive-activity-group__summary";
  summary.textContent = "Ćwiczenia i pytania";

  const content = document.createElement("div");
  content.className = "interactive-activity-group__content";

  details.append(summary, content);
  return { root: details, content };
}
