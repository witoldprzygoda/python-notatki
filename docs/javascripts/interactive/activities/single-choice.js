import { createActivityShell } from "../activity-dom.js";


function previousAttempts(state) {
  return Number.isInteger(state?.attempts) && state.attempts >= 0
    ? state.attempts
    : 0;
}


export function createSingleChoiceProgressState(
  activity,
  previousState,
  selectedOptionId,
) {
  const isCorrect = selectedOptionId === activity.correct_option_id;
  const wasCompleted =
    previousState?.status === "completed" || previousState?.score === 1;
  const completed = wasCompleted || isCorrect;

  return {
    version: activity.version,
    status: completed ? "completed" : "in_progress",
    score: completed ? 1 : 0,
    attempts: previousAttempts(previousState) + 1,
    payload: {
      selected_option_id: selectedOptionId,
      last_result: isCorrect ? "correct" : "incorrect",
    },
  };
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


function clearLocalState(radioButtons, feedback, summary, shell) {
  for (const radio of radioButtons) {
    radio.checked = false;
  }
  clearFeedback(feedback);
  setProgressSummary(summary, null);
  shell.setProgressState("pending");
}


export async function renderSingleChoice({ activity, store, document }) {
  const shell = createActivityShell({
    document,
    activity,
    type: "single-choice",
    typeLabel: "Pytanie jednokrotnego wyboru",
    title: activity.label,
    prompt: activity.prompt,
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
  const restartButton = document.createElement("button");
  restartButton.type = "button";
  restartButton.className = "interactive-activity__button";
  restartButton.textContent = "Zacznij od nowa";
  actions.append(checkButton, restartButton);

  const feedback = document.createElement("p");
  feedback.className = "interactive-activity__message";
  feedback.setAttribute("aria-live", "polite");
  feedback.setAttribute("aria-atomic", "true");
  feedback.hidden = true;

  const summary = document.createElement("p");
  summary.className = "interactive-activity__meta";
  let busy = false;
  let readFailed = false;
  let hasSavedState = false;

  function hasSelectedOption() {
    return radioButtons.some((radio) => radio.checked);
  }

  function updateControls() {
    fieldset.disabled = readFailed || busy;
    checkButton.disabled = readFailed || busy;
    restartButton.disabled =
      readFailed || busy || (!hasSavedState && !hasSelectedOption());
  }

  try {
    const savedState = await store.get(activity.activity_id);
    hasSavedState = savedState !== null;
    restoreState(activity, savedState, radioButtons, feedback, summary);
    shell.setProgressState(
      savedState?.status === "completed" ? "completed" : "pending",
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
      const savedState = await store.save(activity.activity_id, nextState);
      hasSavedState = true;
      showFeedback(activity, nextState.payload.last_result, feedback);
      setProgressSummary(summary, savedState);
      shell.setProgressState(
        savedState.status === "completed" ? "completed" : "pending",
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

  restartButton.addEventListener("click", async () => {
    if (busy || readFailed || (!hasSavedState && !hasSelectedOption())) {
      return;
    }

    if (!hasSavedState) {
      clearLocalState(radioButtons, feedback, summary, shell);
      updateControls();
      radioButtons[0]?.focus?.();
      return;
    }

    busy = true;
    updateControls();
    let resetSucceeded = false;
    try {
      await store.reset([activity.activity_id]);
      hasSavedState = false;
      clearLocalState(radioButtons, feedback, summary, shell);
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
  });

  fieldset.append(legend, options, actions);
  form.append(fieldset);
  shell.interaction.append(form);
  shell.messages.append(feedback, summary);
  return shell.root;
}
