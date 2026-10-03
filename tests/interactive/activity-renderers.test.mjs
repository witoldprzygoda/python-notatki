import assert from "node:assert/strict";
import test from "node:test";

import {
  renderAcknowledgement,
} from "../../docs/javascripts/interactive/activities/acknowledgement.js";
import {
  renderSingleChoice,
} from "../../docs/javascripts/interactive/activities/single-choice.js";
import {
  createFakeDocument,
  dispatch,
  findByClass,
  findElement,
  findElements,
  hasClass,
} from "./support/fake-dom.mjs";


function readOnlyStore(state) {
  return {
    async get() {
      return state;
    },
    async save(activityId, nextState) {
      return { activity_id: activityId, ...nextState };
    },
  };
}


function singleChoiceActivity(activityId = "flow-for-quiz-001") {
  return {
    activity_id: activityId,
    version: 1,
    label: "Sprawdzenie zrozumienia pętli for",
    prompt: "Ile razy wykona się ciało pętli?",
    options: [
      { option_id: "a", label: "Dwa razy" },
      { option_id: "b", label: "Trzy razy" },
      { option_id: "c", label: "Cztery razy" },
    ],
    correct_option_id: "b",
    feedback: {
      correct: "Łańcuch zawiera trzy znaki.",
      incorrect: "Łańcuch zawiera trzy znaki.",
    },
    solution: {
      discussion: "Pętla wykonuje ciało raz dla każdego znaku łańcucha.",
    },
  };
}


function findStateAction(root) {
  const buttons = findElements(
    root,
    (element) => hasClass(element, "interactive-activity__state-action"),
  );
  assert.equal(buttons.length, 1);
  return buttons[0];
}


function mutableStore(
  initialStates = {},
  { resetError = null, saveError = null } = {},
) {
  const states = new Map(Object.entries(initialStates));
  const resetCalls = [];
  const saveCalls = [];

  return {
    states,
    resetCalls,
    saveCalls,
    async get(activityId) {
      const state = states.get(activityId);
      return state ? { ...state, payload: state.payload && { ...state.payload } } : null;
    },
    async save(activityId, nextState) {
      saveCalls.push({ activityId, state: nextState });
      if (saveError) {
        throw saveError;
      }
      const savedState = {
        activity_id: activityId,
        ...nextState,
        payload: nextState.payload && { ...nextState.payload },
        updated_at: "2026-08-21T12:00:00.000Z",
      };
      states.set(activityId, savedState);
      return { ...savedState, payload: { ...savedState.payload } };
    },
    async reset(activityIds = null) {
      resetCalls.push(activityIds === null ? null : [...activityIds]);
      if (resetError) {
        throw resetError;
      }
      if (activityIds === null) {
        states.clear();
        return;
      }
      for (const activityId of activityIds) {
        states.delete(activityId);
      }
    },
  };
}


test("acknowledgement zachowuje natywny checkbox i semantykę fieldset", async () => {
  const document = createFakeDocument();
  const activity = {
    activity_id: "flow-for-read-001",
    version: 1,
    label: "Zapoznałem się z podstawami pętli for",
  };
  const root = await renderAcknowledgement({
    activity,
    store: readOnlyStore({ status: "completed" }),
    document,
  });

  const fieldset = findElement(root, (element) => element.tagName === "fieldset");
  const legend = findElement(root, (element) => element.tagName === "legend");
  const checkbox = findElement(
    root,
    (element) => element.tagName === "input" && element.type === "checkbox",
  );
  const label = findElement(
    root,
    (element) => element.tagName === "label" && element.children.includes(checkbox),
  );
  const prompt = findByClass(root, "interactive-activity__prompt");
  const progress = findByClass(root, "interactive-activity__progress");
  const message = findByClass(root, "interactive-activity__message");

  assert.ok(fieldset);
  assert.equal(fieldset.children[0], legend);
  assert.equal(
    hasClass(legend, "interactive-activity__visually-hidden"),
    true,
  );
  assert.equal(legend.hidden, false);
  assert.equal(fieldset.getAttribute("aria-describedby"), prompt.id);
  assert.ok(label);
  assert.equal(checkbox.checked, true);
  assert.equal(root.dataset.progressState, "completed");
  assert.equal(progress.textContent, "✓ Wykonano");
  assert.equal(progress.getAttribute("aria-live"), null);
  assert.equal(message.getAttribute("aria-live"), "polite");
  assert.equal(message.getAttribute("aria-atomic"), "true");

  assert.equal(
    findElements(
      root,
      (element) => hasClass(element, "interactive-activity__progress"),
    ).length,
    1,
  );
  assert.equal(root.textContent.split(activity.label).length - 1, 1);
  assert.equal(root.textContent.split("✓ Wykonano").length - 1, 1);
});


test("single choice zachowuje formularz, legendę i natywne radio bez br", async () => {
  const document = createFakeDocument();
  const activity = singleChoiceActivity();
  const root = await renderSingleChoice({
    activity,
    store: readOnlyStore({
      status: "completed",
      score: 1,
      attempts: 3,
      payload: {
        selected_option_id: "c",
        last_result: "incorrect",
      },
    }),
    document,
  });

  const form = findElement(root, (element) => element.tagName === "form");
  const fieldset = findElement(root, (element) => element.tagName === "fieldset");
  const legend = findElement(root, (element) => element.tagName === "legend");
  const prompt = findByClass(root, "interactive-activity__prompt");
  const radios = findElements(
    root,
    (element) => element.tagName === "input" && element.type === "radio",
  );
  const checkButton = findElement(
    root,
    (element) => element.tagName === "button" && element.textContent === "Sprawdź",
  );
  const feedback = findByClass(root, "interactive-activity__message");
  const resultLabel = findByClass(
    feedback,
    "interactive-activity__message-result",
  );
  const explanation = findByClass(
    feedback,
    "interactive-activity__message-explanation",
  );
  const progress = findByClass(root, "interactive-activity__progress");
  const summary = findByClass(root, "interactive-activity__meta");
  const header = findByClass(root, "interactive-activity__header");
  const headerState = findByClass(root, "interactive-activity__header-state");
  const stateAction = findStateAction(root);
  const actions = findByClass(root, "interactive-activity__actions");
  const solutionActions = findByClass(
    root,
    "interactive-activity__solution-actions",
  );
  const solutionLabel = findByClass(
    root,
    "interactive-activity__solution-label",
  );
  const solutionButton = findElement(
    root,
    (element) => element.tagName === "button" && element.textContent === "Pokaż",
  );
  const discussionButton = findElement(
    root,
    (element) => element.tagName === "button" && element.textContent === "Omów",
  );

  assert.equal(form.children[0], fieldset);
  assert.equal(fieldset.children[0], legend);
  assert.equal(
    hasClass(legend, "interactive-activity__visually-hidden"),
    true,
  );
  assert.equal(legend.hidden, false);
  assert.equal(fieldset.getAttribute("aria-describedby"), prompt.id);
  assert.equal(findElements(root, (element) => element.tagName === "br").length, 0);
  assert.equal(radios.length, 3);
  assert.equal(new Set(radios.map((radio) => radio.name)).size, 1);
  assert.equal(radios.every((radio) => radio.required), true);
  assert.equal(radios.find((radio) => radio.value === "c").checked, true);
  assert.equal(checkButton.type, "submit");

  assert.equal(root.dataset.progressState, "completed");
  assert.equal(progress.textContent, "✓ Wykonano");
  assert.equal(progress.getAttribute("aria-live"), null);
  assert.equal(feedback.hidden, false);
  assert.equal(
    hasClass(feedback, "interactive-activity__message--incorrect"),
    true,
  );
  assert.equal(resultLabel.textContent, "! Niepoprawnie");
  assert.equal(explanation.textContent, activity.feedback.incorrect);
  assert.equal(feedback.textContent.includes("Ostatnie sprawdzenie"), false);
  assert.equal(feedback.getAttribute("aria-live"), "polite");
  assert.equal(feedback.getAttribute("aria-atomic"), "true");
  assert.equal(summary.textContent, "Próby: 3");
  assert.equal(summary.getAttribute("aria-live"), null);
  assert.equal(headerState.parentNode, header);
  assert.deepEqual(headerState.children, [stateAction, progress]);
  assert.equal(stateAction.getAttribute("type"), "button");
  assert.equal(stateAction.textContent, "Zacznij od nowa");
  assert.equal(
    findElements(
      root,
      (element) => element.tagName === "button"
        && element.textContent === "Zacznij od nowa",
    ).length,
    1,
  );
  assert.deepEqual(actions.children, [checkButton, solutionActions]);
  assert.equal(solutionLabel.textContent, "Rozwiązanie:");
  assert.equal(solutionButton.getAttribute("type"), "button");
  assert.equal(solutionButton.getAttribute("aria-label"), "Pokaż rozwiązanie");
  assert.equal(discussionButton.getAttribute("type"), "button");
  assert.equal(discussionButton.getAttribute("aria-label"), "Omów rozwiązanie");
  assert.equal(findByClass(root, "interactive-activity__help-heading"), undefined);
  assert.equal(root.textContent.includes("Pomoc"), false);
  assert.equal(root.textContent.includes("Pokaż rozwiązanie"), false);
  assert.equal(root.textContent.includes("Omów rozwiązanie"), false);
});


test("Pokaż rozwiązanie kończy single choice bez zmiany wyboru ani wyniku Check", async () => {
  const document = createFakeDocument();
  const activity = singleChoiceActivity();
  const store = mutableStore();
  const root = await renderSingleChoice({ activity, store, document });
  const radios = findElements(
    root,
    (element) => element.tagName === "input" && element.type === "radio",
  );
  const solutionButton = findElement(
    root,
    (element) => element.tagName === "button"
      && element.textContent === "Pokaż",
  );
  const solutionPanel = findElement(
    root,
    (element) => element.dataset.helpPanel === "solution",
  );
  const progress = findByClass(root, "interactive-activity__progress");
  const summary = findByClass(root, "interactive-activity__meta");
  const stateAction = findStateAction(root);

  radios[0].checked = true;
  await dispatch(radios[0], "change");
  assert.equal(stateAction.textContent, "Oznacz jako wykonane");
  await dispatch(solutionButton, "click");

  const saved = store.states.get(activity.activity_id);
  assert.equal(radios[0].checked, true);
  assert.equal(radios[1].checked, false);
  assert.equal(solutionPanel.hidden, false);
  assert.equal(solutionPanel.textContent.includes("Trzy razy"), true);
  assert.equal(saved.status, "completed");
  assert.equal(saved.attempts, 0);
  assert.equal(Object.hasOwn(saved, "score"), false);
  assert.deepEqual(saved.payload, {
    selected_option_id: "a",
    solution_revealed: true,
    completion_method: "solution_shown",
  });
  assert.equal(progress.textContent, "✓ Wykonano");
  assert.equal(summary.textContent, "Próby: 0");
  assert.equal(findStateAction(root), stateAction);
  assert.equal(stateAction.textContent, "Zacznij od nowa");
});


test("błąd zapisu po Pokaż rozwiązanie nie ukrywa treści ani nie udaje completed", async (t) => {
  const document = createFakeDocument();
  const activity = singleChoiceActivity();
  const store = mutableStore({}, { saveError: new Error("save failed") });
  t.mock.method(console, "warn", () => {});
  const root = await renderSingleChoice({ activity, store, document });
  const solutionButton = findElement(
    root,
    (element) => element.tagName === "button"
      && element.textContent === "Pokaż",
  );
  const solutionPanel = findElement(
    root,
    (element) => element.dataset.helpPanel === "solution",
  );
  const feedback = findByClass(root, "interactive-activity__message");
  const progress = findByClass(root, "interactive-activity__progress");
  const stateAction = findStateAction(root);

  await dispatch(solutionButton, "click");

  assert.equal(solutionPanel.hidden, false);
  assert.equal(store.states.has(activity.activity_id), false);
  assert.equal(root.dataset.progressState, "pending");
  assert.equal(progress.textContent, "○ Do wykonania");
  assert.equal(stateAction.textContent, "Oznacz jako wykonane");
  assert.equal(
    hasClass(feedback, "interactive-activity__message--error"),
    true,
  );
  assert.equal(
    feedback.textContent,
    "Błąd techniczny: nie udało się zapisać postępu.",
  );
});


test("niezapisane ujawnienie nie trafia do późniejszego Check", async (t) => {
  const document = createFakeDocument();
  const activity = singleChoiceActivity();
  const store = mutableStore();
  const successfulSave = store.save.bind(store);
  let rejectNextSave = true;
  store.save = async (...args) => {
    if (rejectNextSave) {
      rejectNextSave = false;
      throw new Error("save failed");
    }
    return successfulSave(...args);
  };
  t.mock.method(console, "warn", () => {});
  const root = await renderSingleChoice({ activity, store, document });
  const solutionButton = findElement(
    root,
    (element) => element.tagName === "button"
      && element.textContent === "Pokaż",
  );
  const solutionPanel = findElement(
    root,
    (element) => element.dataset.helpPanel === "solution",
  );
  const form = findElement(root, (element) => element.tagName === "form");
  const radios = findElements(
    root,
    (element) => element.tagName === "input" && element.type === "radio",
  );

  await dispatch(solutionButton, "click");
  radios[0].checked = true;
  await dispatch(radios[0], "change");
  await dispatch(form, "submit", { preventDefault() {} });

  const saved = store.states.get(activity.activity_id);
  assert.equal(solutionPanel.hidden, false);
  assert.equal(saved.status, "in_progress");
  assert.equal(saved.payload.last_result, "incorrect");
  assert.equal(saved.payload.solution_revealed, undefined);
  assert.equal(saved.payload.completion_method, undefined);

  const reloaded = await renderSingleChoice({
    activity,
    store,
    document: createFakeDocument(),
  });
  assert.equal(
    findElement(
      reloaded,
      (element) => element.dataset.helpPanel === "solution",
    ).hidden,
    true,
  );
});


test("ręczne ukończenie po zmianie odpowiedzi usuwa feedback starego Check", async () => {
  const document = createFakeDocument();
  const activity = singleChoiceActivity();
  const store = mutableStore({
    [activity.activity_id]: {
      status: "in_progress",
      score: 0,
      attempts: 1,
      payload: {
        selected_option_id: "a",
        last_result: "incorrect",
        unknown_future_field: "zachowaj",
      },
    },
  });
  const root = await renderSingleChoice({ activity, store, document });
  const radios = findElements(
    root,
    (element) => element.tagName === "input" && element.type === "radio",
  );
  const completionButton = findStateAction(root);

  radios[0].checked = false;
  radios[1].checked = true;
  await dispatch(radios[1], "change");
  await dispatch(completionButton, "click");

  const saved = store.states.get(activity.activity_id);
  assert.equal(saved.payload.selected_option_id, "b");
  assert.equal(saved.payload.last_result, undefined);
  assert.equal(saved.payload.unknown_future_field, "zachowaj");
  assert.equal(saved.payload.completion_method, "self_marked");
});


test("self_marked pozostaje pierwszą metodą po późniejszym poprawnym Check", async () => {
  const document = createFakeDocument();
  const activity = singleChoiceActivity();
  const store = mutableStore();
  const root = await renderSingleChoice({ activity, store, document });
  const form = findElement(root, (element) => element.tagName === "form");
  const radios = findElements(
    root,
    (element) => element.tagName === "input" && element.type === "radio",
  );
  const completionButton = findStateAction(root);

  assert.equal(completionButton.textContent, "Oznacz jako wykonane");
  await dispatch(completionButton, "click");
  const manuallyCompleted = store.states.get(activity.activity_id);
  assert.equal(manuallyCompleted.status, "completed");
  assert.equal(manuallyCompleted.attempts, 0);
  assert.equal(Object.hasOwn(manuallyCompleted, "score"), false);
  assert.equal(manuallyCompleted.payload.completion_method, "self_marked");
  assert.equal(findStateAction(root), completionButton);
  assert.equal(completionButton.textContent, "Zacznij od nowa");

  radios[1].checked = true;
  await dispatch(radios[1], "change");
  await dispatch(form, "submit", { preventDefault() {} });

  const checked = store.states.get(activity.activity_id);
  assert.equal(checked.status, "completed");
  assert.equal(checked.score, 1);
  assert.equal(checked.attempts, 1);
  assert.equal(checked.payload.completion_method, "self_marked");
  assert.equal(checked.payload.last_result, "correct");
});


test("historyczne completed jest odtwarzane bez zapisu i zachowuje implicit checked", async () => {
  const document = createFakeDocument();
  const activity = singleChoiceActivity();
  const store = mutableStore({
    [activity.activity_id]: {
      status: "completed",
      score: 1,
      attempts: 2,
      payload: {
        selected_option_id: "b",
        last_result: "correct",
      },
    },
  });
  const root = await renderSingleChoice({ activity, store, document });
  const solutionButton = findElement(
    root,
    (element) => element.tagName === "button"
      && element.textContent === "Pokaż",
  );

  assert.deepEqual(store.saveCalls, []);
  assert.equal(
    Object.hasOwn(
      store.states.get(activity.activity_id).payload,
      "completion_method",
    ),
    false,
  );

  await dispatch(solutionButton, "click");

  const saved = store.states.get(activity.activity_id);
  assert.equal(saved.payload.completion_method, "checked");
  assert.equal(saved.payload.solution_revealed, true);
  assert.equal(saved.attempts, 2);
  assert.equal(saved.score, 1);
});


test("Zacznij od nowa usuwa ujawnienia i metadane ukończenia single choice", async () => {
  const document = createFakeDocument();
  const activity = singleChoiceActivity();
  const store = mutableStore({
    [activity.activity_id]: {
      status: "completed",
      attempts: 0,
      payload: {
        completion_method: "solution_shown",
        solution_revealed: true,
        discussion_revealed: true,
        unknown_future_field: "preserved-before-reset",
      },
    },
  });
  const root = await renderSingleChoice({ activity, store, document });
  const solutionPanel = findElement(
    root,
    (element) => element.dataset.helpPanel === "solution",
  );
  const discussionPanel = findElement(
    root,
    (element) => element.dataset.helpPanel === "discussion",
  );
  const restartButton = findStateAction(root);

  assert.equal(solutionPanel.hidden, false);
  assert.equal(discussionPanel.hidden, false);
  assert.equal(restartButton.textContent, "Zacznij od nowa");
  await dispatch(restartButton, "click");

  assert.equal(store.states.has(activity.activity_id), false);
  assert.equal(solutionPanel.hidden, true);
  assert.equal(discussionPanel.hidden, true);
  assert.equal(root.dataset.progressState, "pending");
  assert.equal(findByClass(root, "interactive-activity__meta").textContent, "Próby: 0");
  assert.equal(findStateAction(root), restartButton);
  assert.equal(restartButton.textContent, "Oznacz jako wykonane");
  assert.equal(
    findElements(
      root,
      (element) => element.tagName === "button"
        && element.textContent === "Zacznij od nowa",
    ).length,
    0,
  );
});


test("akcja nagłówka w pending zapisuje self_marked bez resetowania wyboru", async () => {
  const document = createFakeDocument();
  const activity = singleChoiceActivity();
  const store = mutableStore();
  const root = await renderSingleChoice({ activity, store, document });
  const radios = findElements(
    root,
    (element) => element.tagName === "input" && element.type === "radio",
  );
  const stateAction = findStateAction(root);
  const progress = findByClass(root, "interactive-activity__progress");
  const summary = findByClass(root, "interactive-activity__meta");
  let stateActionFocused = false;
  stateAction.focus = () => {
    stateActionFocused = true;
  };

  assert.equal(stateAction.type, "button");
  assert.equal(stateAction.textContent, "Oznacz jako wykonane");
  assert.equal(stateAction.disabled, false);
  radios[0].checked = true;
  await dispatch(radios[0], "change");

  await dispatch(stateAction, "click");

  assert.deepEqual(store.resetCalls, []);
  assert.equal(store.saveCalls.length, 1);
  assert.equal(radios[0].checked, true);
  assert.equal(store.states.get(activity.activity_id).status, "completed");
  assert.equal(store.states.get(activity.activity_id).attempts, 0);
  assert.equal(
    Object.hasOwn(store.states.get(activity.activity_id), "score"),
    false,
  );
  assert.deepEqual(store.states.get(activity.activity_id).payload, {
    selected_option_id: "a",
    completion_method: "self_marked",
  });
  assert.equal(summary.textContent, "Próby: 0");
  assert.equal(root.dataset.progressState, "completed");
  assert.equal(progress.textContent, "✓ Wykonano");
  assert.equal(findStateAction(root), stateAction);
  assert.equal(stateAction.textContent, "Zacznij od nowa");
  assert.equal(stateActionFocused, true);
});


test("single choice po resecie odtwarza pusty stan i następną próbę liczy od jednego", async () => {
  const document = createFakeDocument();
  const activity = singleChoiceActivity();
  const otherActivityId = "flow-for-code-001";
  const store = mutableStore({
    [activity.activity_id]: {
      status: "completed",
      score: 1,
      attempts: 3,
      payload: {
        selected_option_id: "b",
        last_result: "correct",
      },
    },
    [otherActivityId]: { status: "completed", score: 1, attempts: 1 },
  });
  const root = await renderSingleChoice({ activity, store, document });
  const radios = findElements(
    root,
    (element) => element.tagName === "input" && element.type === "radio",
  );
  const restartButton = findStateAction(root);
  const feedback = findByClass(root, "interactive-activity__message");
  const progress = findByClass(root, "interactive-activity__progress");
  const summary = findByClass(root, "interactive-activity__meta");
  let firstRadioFocused = false;
  radios[0].focus = () => {
    firstRadioFocused = true;
  };

  await dispatch(restartButton, "click");

  assert.deepEqual(store.resetCalls, [[activity.activity_id]]);
  assert.equal(store.states.has(activity.activity_id), false);
  assert.equal(store.states.has(otherActivityId), true);
  assert.equal(radios.every((radio) => !radio.checked), true);
  assert.equal(feedback.hidden, true);
  assert.equal(summary.textContent, "Próby: 0");
  assert.equal(root.dataset.progressState, "pending");
  assert.equal(progress.textContent, "○ Do wykonania");
  assert.equal(firstRadioFocused, true);

  const reloadedRoot = await renderSingleChoice({ activity, store, document });
  const reloadedForm = findElement(
    reloadedRoot,
    (element) => element.tagName === "form",
  );
  const reloadedRadios = findElements(
    reloadedRoot,
    (element) => element.tagName === "input" && element.type === "radio",
  );
  const reloadedFeedback = findByClass(
    reloadedRoot,
    "interactive-activity__message",
  );
  const reloadedSummary = findByClass(
    reloadedRoot,
    "interactive-activity__meta",
  );
  const reloadedStateAction = findStateAction(reloadedRoot);

  assert.equal(reloadedRadios.every((radio) => !radio.checked), true);
  assert.equal(reloadedFeedback.hidden, true);
  assert.equal(reloadedSummary.textContent, "Próby: 0");
  assert.equal(reloadedRoot.dataset.progressState, "pending");
  assert.equal(reloadedStateAction.textContent, "Oznacz jako wykonane");
  assert.equal(reloadedStateAction.disabled, false);

  reloadedRadios[0].checked = true;
  await dispatch(reloadedRadios[0], "change");
  await dispatch(reloadedForm, "submit", { preventDefault() {} });

  assert.equal(store.saveCalls.length, 1);
  assert.equal(store.saveCalls[0].state.attempts, 1);
  assert.equal(store.states.get(activity.activity_id).attempts, 1);
  assert.equal(reloadedSummary.textContent, "Próby: 1");
  assert.equal(store.states.has(otherActivityId), true);
});


test("błąd resetu zachowuje stan single choice i pozostaje błędem technicznym", async (t) => {
  const document = createFakeDocument();
  const activity = singleChoiceActivity();
  const resetError = new Error("reset failed");
  const store = mutableStore({
    [activity.activity_id]: {
      status: "completed",
      score: 1,
      attempts: 3,
      payload: {
        selected_option_id: "c",
        last_result: "incorrect",
      },
    },
  }, { resetError });
  t.mock.method(console, "warn", () => {});
  const root = await renderSingleChoice({ activity, store, document });
  const fieldset = findElement(root, (element) => element.tagName === "fieldset");
  const radios = findElements(
    root,
    (element) => element.tagName === "input" && element.type === "radio",
  );
  const restartButton = findStateAction(root);
  const feedback = findByClass(root, "interactive-activity__message");
  const progress = findByClass(root, "interactive-activity__progress");
  const summary = findByClass(root, "interactive-activity__meta");

  await dispatch(restartButton, "click");

  assert.deepEqual(store.resetCalls, [[activity.activity_id]]);
  assert.equal(store.states.has(activity.activity_id), true);
  assert.equal(radios.find((radio) => radio.value === "c").checked, true);
  assert.equal(root.dataset.progressState, "completed");
  assert.equal(progress.textContent, "✓ Wykonano");
  assert.equal(summary.textContent, "Próby: 3");
  assert.equal(
    hasClass(feedback, "interactive-activity__message--error"),
    true,
  );
  assert.equal(
    hasClass(feedback, "interactive-activity__message--incorrect"),
    false,
  );
  assert.equal(
    feedback.textContent,
    "Błąd techniczny: nie udało się rozpocząć aktywności od nowa.",
  );
  assert.equal(fieldset.disabled, false);
  assert.equal(restartButton.disabled, false);
  assert.equal(restartButton.textContent, "Zacznij od nowa");
});


test("single choice nie uruchamia Check równolegle z trwającym resetem", async () => {
  const document = createFakeDocument();
  const activity = singleChoiceActivity();
  const store = mutableStore({
    [activity.activity_id]: {
      status: "completed",
      score: 1,
      attempts: 1,
      payload: {
        selected_option_id: "b",
        last_result: "correct",
      },
    },
  });
  let releaseReset;
  store.reset = async (activityIds) => {
    store.resetCalls.push([...activityIds]);
    await new Promise((resolve) => {
      releaseReset = resolve;
    });
    for (const activityId of activityIds) {
      store.states.delete(activityId);
    }
  };
  const root = await renderSingleChoice({ activity, store, document });
  const form = findElement(root, (element) => element.tagName === "form");
  const fieldset = findElement(root, (element) => element.tagName === "fieldset");
  const checkButton = findElement(
    root,
    (element) => element.tagName === "button" && element.textContent === "Sprawdź",
  );
  const restartButton = findStateAction(root);

  const pendingReset = dispatch(restartButton, "click");
  await Promise.resolve();
  assert.equal(fieldset.disabled, true);
  assert.equal(checkButton.disabled, true);
  assert.equal(restartButton.disabled, true);

  await dispatch(form, "submit", { preventDefault() {} });
  assert.deepEqual(store.saveCalls, []);

  releaseReset();
  await pendingReset;
  assert.equal(fieldset.disabled, false);
  assert.equal(checkButton.disabled, false);
});
