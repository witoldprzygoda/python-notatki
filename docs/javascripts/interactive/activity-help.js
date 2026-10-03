function activityHelpDomId(activityId) {
  return `interactive-activity-${encodeURIComponent(String(activityId))}-help`;
}


export function createActivityHelp({
  document,
  activityId,
  solutionContent,
  discussionContent,
}) {
  const baseId = activityHelpDomId(activityId);

  const actions = document.createElement("div");
  actions.className = "interactive-activity__solution-actions";
  actions.setAttribute("role", "group");

  const label = document.createElement("span");
  label.id = `${baseId}-label`;
  label.className = "interactive-activity__solution-label";
  label.textContent = "Rozwiązanie:";
  actions.setAttribute("aria-labelledby", label.id);

  const solutionButton = createRevealButton({
    document,
    id: `${baseId}-solution-button`,
    label: "Pokaż",
    accessibleLabel: "Pokaż rozwiązanie",
    panelId: `${baseId}-solution-panel`,
  });
  const discussionButton = createRevealButton({
    document,
    id: `${baseId}-discussion-button`,
    label: "Omów",
    accessibleLabel: "Omów rozwiązanie",
    panelId: `${baseId}-discussion-panel`,
  });
  actions.append(label, solutionButton, discussionButton);

  const solutionPanel = createPanel({
    document,
    id: solutionButton.getAttribute("aria-controls"),
    labelledBy: solutionButton.id,
    kind: "solution",
    content: solutionContent,
  });
  const discussionPanel = createPanel({
    document,
    id: discussionButton.getAttribute("aria-controls"),
    labelledBy: discussionButton.id,
    kind: "discussion",
    content: discussionContent,
  });

  const panels = document.createElement("div");
  panels.className = "interactive-activity__help-panels";
  panels.append(solutionPanel, discussionPanel);

  let solutionRevealed = false;
  let discussionRevealed = false;
  let busy = false;

  function revealSolution({ focus = false } = {}) {
    const newlyRevealed = !solutionRevealed;
    solutionRevealed = true;
    solutionPanel.hidden = false;
    solutionButton.setAttribute("aria-expanded", "true");
    if (focus && newlyRevealed) {
      solutionPanel.focus?.();
    }
  }

  function revealDiscussion({ focus = false } = {}) {
    revealSolution();
    const newlyRevealed = !discussionRevealed;
    discussionRevealed = true;
    discussionPanel.hidden = false;
    discussionButton.setAttribute("aria-expanded", "true");
    if (focus && newlyRevealed) {
      discussionPanel.focus?.();
    }
  }

  function restoreRevealState({
    solutionRevealed: restoreSolution = false,
    discussionRevealed: restoreDiscussion = false,
  } = {}) {
    if (restoreDiscussion) {
      revealDiscussion();
    } else if (restoreSolution) {
      revealSolution();
    }
  }

  function resetLocalRevealState() {
    solutionRevealed = false;
    discussionRevealed = false;
    solutionPanel.hidden = true;
    discussionPanel.hidden = true;
    solutionButton.setAttribute("aria-expanded", "false");
    discussionButton.setAttribute("aria-expanded", "false");
  }

  function updateDisabledState() {
    solutionButton.disabled = busy;
    discussionButton.disabled = busy;
  }

  function setBusy(nextBusy) {
    busy = Boolean(nextBusy);
    updateDisabledState();
  }

  solutionButton.addEventListener("click", () => {
    revealSolution({ focus: true });
  });
  discussionButton.addEventListener("click", () => {
    revealDiscussion({ focus: true });
  });

  resetLocalRevealState();
  updateDisabledState();

  return {
    actions,
    panels,
    solutionButton,
    discussionButton,
    solutionPanel,
    discussionPanel,
    revealSolution,
    revealDiscussion,
    restoreRevealState,
    resetLocalRevealState,
    setBusy,
  };
}


function createRevealButton({
  document,
  id,
  label,
  accessibleLabel,
  panelId,
}) {
  const button = document.createElement("button");
  button.id = id;
  button.type = "button";
  button.setAttribute("type", "button");
  button.className =
    "interactive-activity__button interactive-activity__help-button";
  button.textContent = label;
  button.setAttribute("aria-label", accessibleLabel);
  button.setAttribute("aria-controls", panelId);
  button.setAttribute("aria-expanded", "false");
  return button;
}


function createPanel({ document, id, labelledBy, kind, content }) {
  const panel = document.createElement("div");
  panel.id = id;
  panel.className = "interactive-activity__help-panel";
  panel.dataset.helpPanel = kind;
  panel.hidden = true;
  panel.setAttribute("role", "region");
  panel.setAttribute("aria-labelledby", labelledBy);
  panel.setAttribute("tabindex", "-1");
  panel.append(content);
  return panel;
}
