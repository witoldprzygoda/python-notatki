import { createActivityShell } from "../activity-dom.js";
import { createActivityHelp } from "../activity-help.js";
import {
  createCheckedProgressState,
  createManualCompletionProgressState,
  isCompleted,
} from "../activity-progress-state.js";


function previousAttempts(state) {
  return Number.isInteger(state?.attempts) && state.attempts >= 0
    ? state.attempts
    : 0;
}


export function createSingleChoiceProgressState(
  activity,
  previousState,
  selectedOptionId,
  payloadPatch = {},
) {
  const isCorrect = selectedOptionId === activity.correct_option_id;
  return createCheckedProgressState(activity, previousState, {
    isCorrect,
    payloadPatch: {
      ...payloadPatch,
      selected_option_id: selectedOptionId,
      last_result: isCorrect ? "correct" : "incorrect",
    },
  });
}


function createSingleChoiceSolutionContent(document, activity) {
  const content = document.createElement("div");
  content.className = "interactive-activity__solution";

  const label = document.createElement("strong");
  label.className = "interactive-activity__solution-heading";
  label.textContent = "Poprawna odpowiedź";

  const answer = document.createElement("p");
  answer.className = "interactive-activity__solution-answer";
  answer.textContent = activity.options.find(
    (option) => option.option_id === activity.correct_option_id,
  )?.label ?? "";

  content.append(label, answer);
  return content;
}


function createSingleChoiceDiscussionContent(document, activity) {
  const content = document.createElement("div");
  content.className = "interactive-activity__discussion";

  const label = document.createElement("strong");
  label.className = "interactive-activity__solution-heading";
  label.textContent = "Dlaczego ta odpowiedź jest poprawna";

  const discussion = document.createElement("p");
  discussion.className = "interactive-activity__discussion-text";
  discussion.textContent = activity.solution.discussion;

  content.append(label, discussion);
  return content;
}


function setProgressSummary(element, state) {
  const attempts = previousAttempts(state);
  element.textContent = `Próby: ${attempts}`;
}


function clearFeedback(feedback) {
  feedback.className = "interactive-activity__message";
  feedback.textContent = "";
  feedback.hidden = true;
}


function showFeedback(activity, result, feedback) {
  const correct = result === "correct";
  feedback.className =
    `interactive-activity__message interactive-activity__message--${result}`;

  const resultLabel = feedback.ownerDocument.createElement("strong");
  resultLabel.className = "interactive-activity__message-result";
  resultLabel.textContent = correct ? "✓ Poprawnie" : "! Niepoprawnie";

  const explanation = feedback.ownerDocument.createElement("span");
  explanation.className = "interactive-activity__message-explanation";
  explanation.textContent = correct
    ? activity.feedback.correct
    : activity.feedback.incorrect;

  feedback.replaceChildren(resultLabel, explanation);
  feedback.hidden = false;
}


function showTechnicalError(feedback, text) {
  feedback.className =
    "interactive-activity__message interactive-activity__message--error";
  feedback.textContent = `Błąd techniczny: ${text}`;
  feedback.hidden = false;
}


function restoreState(activity, state, radioButtons, feedback, summary) {
  const selectedOptionId = state?.payload?.selected_option_id;
  const selectedRadio = radioButtons.find(
    (radio) => radio.value === selectedOptionId,
  );
  if (selectedRadio) {
    selectedRadio.checked = true;
  }

  const lastResult = state?.payload?.last_result;
  if (lastResult === "correct" || lastResult === "incorrect") {
    showFeedback(activity, lastResult, feedback);
  }
  setProgressSummary(summary, state);
}


function clearLocalState(radioButtons, feedback, summary, shell, help) {
  for (const radio of radioButtons) {
    radio.checked = false;
  }
  clearFeedback(feedback);
  setProgressSummary(summary, null);
  shell.setProgressState("pending");
  help.resetLocalRevealState();
}


export async function renderSingleChoice({ activity, store, document }) {
  const shell = createActivityShell({
    document,
    activity,
    type: "single-choice",
    typeLabel: "Pytanie jednokrotnego wyboru",
    title: activity.label,
    prompt: activity.prompt,
    stateAction: true,
  });

  const form = document.createElement("form");
  form.className = "interactive-activity__form";

  const fieldset = document.createElement("fieldset");
  fieldset.className = "interactive-activity__fieldset";
  fieldset.setAttribute("aria-describedby", shell.promptId);
  const legend = document.createElement("legend");
  legend.className = "interactive-activity__visually-hidden";
  legend.textContent = "Wybierz jedną odpowiedź";

  const options = document.createElement("div");
  options.className = "interactive-activity__options";

  const groupName = `single-choice-${activity.activity_id}`;
  const radioButtons = [];
  for (const option of activity.options) {
    const optionLabel = document.createElement("label");
    optionLabel.className = "interactive-activity__option";
    const radio = document.createElement("input");
    radio.type = "radio";
    radio.name = groupName;
    radio.value = option.option_id;
    radio.required = true;
    const optionText = document.createElement("span");
    optionText.textContent = option.label;
    optionLabel.append(radio, optionText);
    options.append(optionLabel);
    radioButtons.push(radio);
  }

  const actions = document.createElement("div");
  actions.className = "interactive-activity__actions";
  const checkButton = document.createElement("button");
  checkButton.type = "submit";
  checkButton.className =
    "interactive-activity__button interactive-activity__button--primary";
  checkButton.textContent = "Sprawdź";
  actions.append(checkButton);

  const feedback = document.createElement("p");
  feedback.className = "interactive-activity__message";
  feedback.setAttribute("aria-live", "polite");
  feedback.setAttribute("aria-atomic", "true");
  feedback.hidden = true;

  const summary = document.createElement("p");
  summary.className = "interactive-activity__meta";
  const help = createActivityHelp({
    document,
    activityId: activity.activity_id,
    solutionContent: createSingleChoiceSolutionContent(document, activity),
    discussionContent: createSingleChoiceDiscussionContent(document, activity),
  });
  actions.append(help.actions);
  let busy = false;
  let readFailed = false;
  let hasSavedState = false;
  let savedState = null;
  let localSolutionRevealed = false;
  let localDiscussionRevealed = false;

  function currentPayloadPatch(extra = {}) {
    const selectedRadio = radioButtons.find((radio) => radio.checked);
    return {
      ...(selectedRadio
        ? { selected_option_id: selectedRadio.value }
        : {}),
      ...(localSolutionRevealed ? { solution_revealed: true } : {}),
      ...(localDiscussionRevealed ? { discussion_revealed: true } : {}),
      ...extra,
    };
  }

  function updateControls() {
    fieldset.disabled = readFailed || busy;
    checkButton.disabled = readFailed || busy;
    help.setBusy(busy);
    shell.stateActionButton.disabled = readFailed || busy;
  }

  try {
    savedState = await store.get(activity.activity_id);
    hasSavedState = savedState !== null;
    restoreState(activity, savedState, radioButtons, feedback, summary);
    localSolutionRevealed =
      savedState?.payload?.solution_revealed === true
      || savedState?.payload?.discussion_revealed === true;
    localDiscussionRevealed =
      savedState?.payload?.discussion_revealed === true;
    help.restoreRevealState({
      solutionRevealed: localSolutionRevealed,
      discussionRevealed: localDiscussionRevealed,
    });
    shell.setProgressState(
      isCompleted(savedState) ? "completed" : "pending",
    );
  } catch (error) {
    readFailed = true;
    shell.setProgressState("unknown");
    setProgressSummary(summary, null);
    showTechnicalError(
      feedback,
      "nie można odczytać lokalnego stanu aktywności.",
    );
    console.warn("Nie udało się odczytać postępu aktywności.", error);
  }
  updateControls();

  for (const radio of radioButtons) {
    radio.addEventListener("change", () => {
      clearFeedback(feedback);
      updateControls();
    });
  }

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (busy || readFailed) {
      return;
    }
    const selectedRadio = radioButtons.find((radio) => radio.checked);
    if (!selectedRadio) {
      return;
    }

    busy = true;
    updateControls();
    try {
      const currentState = await store.get(activity.activity_id);
      const nextState = createSingleChoiceProgressState(
        activity,
        currentState,
        selectedRadio.value,
      );
      savedState = await store.save(activity.activity_id, nextState);
      hasSavedState = true;
      showFeedback(activity, nextState.payload.last_result, feedback);
      setProgressSummary(summary, savedState);
      shell.setProgressState(
        isCompleted(savedState) ? "completed" : "pending",
      );
    } catch (error) {
      showTechnicalError(
        feedback,
        "nie udało się zapisać lokalnego stanu aktywności.",
      );
      console.warn("Nie udało się zapisać postępu aktywności.", error);
    } finally {
      busy = false;
      updateControls();
    }
  });

  async function saveManualCompletion(completionMethod) {
    if (busy || readFailed) {
      return;
    }

    busy = true;
    updateControls();
    try {
      const currentState = await store.get(activity.activity_id);
      const selectedRadio = radioButtons.find((radio) => radio.checked);
      const selectionChanged = Boolean(selectedRadio)
        && selectedRadio.value !== currentState?.payload?.selected_option_id;
      const nextState = createManualCompletionProgressState(
        activity,
        currentState,
        {
          completionMethod,
          payloadPatch: currentPayloadPatch(),
          removePayloadKeys: selectionChanged ? ["last_result"] : [],
        },
      );
      savedState = await store.save(activity.activity_id, nextState);
      hasSavedState = true;
      setProgressSummary(summary, savedState);
      shell.setProgressState(
        isCompleted(savedState) ? "completed" : "pending",
      );
      if (feedback.className.includes("interactive-activity__message--error")) {
        clearFeedback(feedback);
      }
    } catch (error) {
      showTechnicalError(feedback, "nie udało się zapisać postępu.");
      console.warn("Nie udało się zapisać postępu aktywności.", error);
    } finally {
      busy = false;
      updateControls();
    }
  }

  help.solutionButton.addEventListener("click", async () => {
    localSolutionRevealed = true;
    updateControls();
    if (savedState?.payload?.solution_revealed === true) {
      return;
    }
    await saveManualCompletion("solution_shown");
  });

  help.discussionButton.addEventListener("click", async () => {
    localSolutionRevealed = true;
    localDiscussionRevealed = true;
    updateControls();
    if (savedState?.payload?.discussion_revealed === true) {
      return;
    }
    await saveManualCompletion("solution_shown");
  });

  async function restartActivity() {
    if (busy || readFailed || !hasSavedState || !isCompleted(savedState)) {
      return;
    }

    busy = true;
    updateControls();
    let resetSucceeded = false;
    try {
      await store.reset([activity.activity_id]);
      hasSavedState = false;
      savedState = null;
      localSolutionRevealed = false;
      localDiscussionRevealed = false;
      clearLocalState(radioButtons, feedback, summary, shell, help);
      resetSucceeded = true;
    } catch (error) {
      showTechnicalError(
        feedback,
        "nie udało się rozpocząć aktywności od nowa.",
      );
      console.warn("Nie udało się wyzerować postępu aktywności.", error);
    } finally {
      busy = false;
      updateControls();
      if (resetSucceeded) {
        radioButtons[0]?.focus?.();
      }
    }
  }

  shell.stateActionButton.addEventListener("click", async () => {
    if (busy || readFailed) {
      return;
    }
    if (isCompleted(savedState)) {
      await restartActivity();
      return;
    }

    await saveManualCompletion("self_marked");
    if (isCompleted(savedState)) {
      shell.stateActionButton.focus?.();
    }
  });

  fieldset.append(legend, options);
  form.append(fieldset, actions, help.panels);
  shell.interaction.append(form);
  shell.messages.append(feedback, summary);
  return shell.root;
}
