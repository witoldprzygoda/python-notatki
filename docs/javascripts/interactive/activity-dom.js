function activityDomId(activityId) {
  const encodedId = encodeURIComponent(String(activityId));
  return `interactive-activity-${encodedId}`;
}


export function createActivityShell({
  document,
  activity,
  type,
  typeLabel,
  title,
  prompt,
  stateAction = false,
}) {
  const root = document.createElement("section");
  root.className = `interactive-activity interactive-activity--${type}`;
  root.dataset.activityId = activity.activity_id;
  root.dataset.activityType = type;
  root.dataset.progressState = "pending";

  const baseId = activityDomId(activity.activity_id);
  const titleId = `${baseId}-title`;
  const promptId = `${baseId}-prompt`;
  root.setAttribute("aria-labelledby", titleId);

  const header = document.createElement("header");
  header.className = "interactive-activity__header";

  const heading = document.createElement("div");
  heading.className = "interactive-activity__heading";

  const typeElement = document.createElement("div");
  typeElement.className = "interactive-activity__type";
  typeElement.textContent = typeLabel;

  const titleElement = document.createElement("div");
  titleElement.id = titleId;
  titleElement.className = "interactive-activity__title";
  titleElement.textContent = title;

  const progress = document.createElement("div");
  progress.className =
    "interactive-activity__header-control interactive-activity__progress";
  progress.textContent = "○ Do wykonania";

  let stateActionButton = null;
  let headerState = null;
  if (stateAction) {
    headerState = document.createElement("div");
    headerState.className = "interactive-activity__header-state";

    stateActionButton = document.createElement("button");
    stateActionButton.type = "button";
    stateActionButton.setAttribute("type", "button");
    stateActionButton.className =
      "interactive-activity__button interactive-activity__header-control "
      + "interactive-activity__state-action";
    stateActionButton.textContent = "Oznacz jako wykonane";

    headerState.append(stateActionButton, progress);
  }

  heading.append(typeElement, titleElement);
  header.append(heading, headerState ?? progress);

  const body = document.createElement("div");
  body.className = "interactive-activity__body";

  const promptElement = document.createElement("p");
  promptElement.id = promptId;
  promptElement.className = "interactive-activity__prompt";
  const promptLabel = document.createElement("strong");
  promptLabel.textContent = "Polecenie:";
  const promptText = document.createElement("span");
  promptText.textContent = ` ${prompt}`;
  promptElement.append(promptLabel, promptText);

  const interaction = document.createElement("div");
  interaction.className = "interactive-activity__interaction";

  const messages = document.createElement("div");
  messages.className = "interactive-activity__messages";

  body.append(promptElement, interaction, messages);
  root.append(header, body);

  function setProgressState(state) {
    root.dataset.progressState = state;
    if (state === "completed") {
      progress.textContent = "✓ Wykonano";
      if (stateActionButton) {
        stateActionButton.textContent = "Zacznij od nowa";
      }
    } else if (state === "unknown") {
      progress.textContent = "— Stan niedostępny";
      if (stateActionButton) {
        stateActionButton.textContent = "Oznacz jako wykonane";
      }
    } else {
      progress.textContent = "○ Do wykonania";
      if (stateActionButton) {
        stateActionButton.textContent = "Oznacz jako wykonane";
      }
    }
  }

  return {
    root,
    body,
    interaction,
    messages,
    progress,
    stateActionButton,
    prompt: promptElement,
    promptId,
    title: titleElement,
    setProgressState,
  };
}
