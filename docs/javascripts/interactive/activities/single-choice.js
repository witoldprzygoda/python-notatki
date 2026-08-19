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
  const completion = state?.status === "completed"
    ? " Aktywność ukończona."
    : "";
  element.textContent = `Liczba prób: ${attempts}.${completion}`;
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
    feedback.textContent = activity.feedback[lastResult];
    feedback.hidden = false;
  }
  setProgressSummary(summary, state);
}


export async function renderSingleChoice({ activity, store, document }) {
  const form = document.createElement("form");
  form.className = "interactive-activity interactive-activity--single-choice";
  form.dataset.activityId = activity.activity_id;

  const fieldset = document.createElement("fieldset");
  const legend = document.createElement("legend");
  legend.textContent = activity.label;
  const prompt = document.createElement("p");
  prompt.textContent = activity.prompt;
  fieldset.append(legend, prompt);

  const groupName = `single-choice-${activity.activity_id}`;
  const radioButtons = [];
  for (const option of activity.options) {
    const optionLabel = document.createElement("label");
    const radio = document.createElement("input");
    radio.type = "radio";
    radio.name = groupName;
    radio.value = option.option_id;
    radio.required = true;
    const optionText = document.createElement("span");
    optionText.textContent = option.label;
    optionLabel.append(radio, document.createTextNode(" "), optionText);
    fieldset.append(optionLabel, document.createElement("br"));
    radioButtons.push(radio);
  }

  const checkButton = document.createElement("button");
  checkButton.type = "submit";
  checkButton.textContent = "Sprawdź";

  const feedback = document.createElement("p");
  feedback.setAttribute("aria-live", "polite");
  feedback.hidden = true;

  const summary = document.createElement("p");
  let savedState = null;
  try {
    savedState = await store.get(activity.activity_id);
    restoreState(activity, savedState, radioButtons, feedback, summary);
  } catch (error) {
    fieldset.disabled = true;
    summary.textContent = "Nie można odczytać lokalnego stanu aktywności.";
    console.warn("Nie udało się odczytać postępu aktywności.", error);
  }

  for (const radio of radioButtons) {
    radio.addEventListener("change", () => {
      feedback.textContent = "";
      feedback.hidden = true;
    });
  }

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const selectedRadio = radioButtons.find((radio) => radio.checked);
    if (!selectedRadio) {
      return;
    }

    checkButton.disabled = true;
    try {
      const currentState = await store.get(activity.activity_id);
      const nextState = createSingleChoiceProgressState(
        activity,
        currentState,
        selectedRadio.value,
      );
      savedState = await store.save(activity.activity_id, nextState);
      feedback.textContent = activity.feedback[nextState.payload.last_result];
      feedback.hidden = false;
      setProgressSummary(summary, savedState);
    } catch (error) {
      feedback.textContent = "Nie udało się zapisać lokalnego stanu aktywności.";
      feedback.hidden = false;
      console.warn("Nie udało się zapisać postępu aktywności.", error);
    } finally {
      checkButton.disabled = false;
    }
  });

  fieldset.append(checkButton, feedback, summary);
  form.append(fieldset);
  return form;
}
