import assert from "node:assert/strict";
import test from "node:test";

import {
  createCheckedProgressState,
  createCodeRunProgressState,
  createManualCompletionProgressState,
  getCompletionMethod,
  isCompleted,
  mergeProgressPayload,
} from "../../docs/javascripts/interactive/activity-progress-state.js";


const activity = {
  activity_id: "activity-001",
  version: 3,
};


test("isCompleted opiera się wyłącznie na statusie", () => {
  assert.equal(isCompleted({ status: "completed", score: 0 }), true);
  assert.equal(isCompleted({ status: "in_progress", score: 1 }), false);
  assert.equal(isCompleted(null), false);
});


test("legacy completion_method jest odczytywane jako checked bez mutacji stanu", () => {
  const legacyState = {
    status: "completed",
    score: 1,
    payload: {},
  };

  assert.equal(getCompletionMethod(legacyState), "checked");
  assert.equal(legacyState.payload.completion_method, undefined);
  assert.equal(
    getCompletionMethod({ status: "in_progress", score: 1, payload: {} }),
    null,
  );
  assert.equal(
    getCompletionMethod({
      status: "in_progress",
      payload: { completion_method: "self_marked" },
    }),
    null,
  );
});


test("payload jest scalany płytko, zachowuje obce pola i pozwala je usunąć", () => {
  const previousState = {
    payload: {
      source_code: "stary kod",
      solution_revealed: true,
      unknown_metadata: { retained: true },
      remove_me: "wartość",
    },
  };
  const snapshot = structuredClone(previousState);

  const payload = mergeProgressPayload(
    previousState,
    { source_code: "nowy kod", added: 1 },
    ["remove_me"],
  );

  assert.deepEqual(payload, {
    source_code: "nowy kod",
    solution_revealed: true,
    unknown_metadata: { retained: true },
    added: 1,
  });
  assert.deepEqual(previousState, snapshot);
});


test("poprawny Check zwiększa attempts raz, ustawia najlepszy wynik i metodę checked", () => {
  const state = createCheckedProgressState(activity, {
    status: "in_progress",
    score: 0,
    attempts: 2,
    payload: { reveal_available: true },
  }, {
    isCorrect: true,
    payloadPatch: { last_result: "correct" },
  });

  assert.deepEqual(state, {
    version: 3,
    status: "completed",
    score: 1,
    attempts: 3,
    payload: {
      reveal_available: true,
      last_result: "correct",
      completion_method: "checked",
    },
  });
});


test("błędny Check nie cofa completed, zachowuje najlepszy wynik i pierwszą metodę", () => {
  const previousState = {
    version: 2,
    status: "completed",
    score: 1,
    attempts: 4,
    payload: {
      completion_method: "self_marked",
      solution_revealed: true,
    },
  };
  const snapshot = structuredClone(previousState);

  const state = createCheckedProgressState(activity, previousState, {
    isCorrect: false,
    payloadPatch: { last_result: "incorrect" },
  });

  assert.deepEqual(state, {
    version: 3,
    status: "completed",
    score: 1,
    attempts: 5,
    payload: {
      completion_method: "self_marked",
      solution_revealed: true,
      last_result: "incorrect",
    },
  });
  assert.deepEqual(previousState, snapshot);
});


test("błędny Check zapisuje score 0 nawet bez wcześniejszego wyniku", () => {
  const state = createCheckedProgressState(activity, null, {
    isCorrect: false,
  });

  assert.deepEqual(state, {
    version: 3,
    status: "in_progress",
    score: 0,
    attempts: 1,
    payload: {},
  });
});


test("ręczne ukończenie zachowuje attempts i nie syntetyzuje score", () => {
  const state = createManualCompletionProgressState(activity, {
    status: "in_progress",
    attempts: 2,
    payload: { solution_revealed: true, unknown: "zachowaj" },
  }, {
    completionMethod: "solution_shown",
    payloadPatch: { solution_revealed: true },
  });

  assert.deepEqual(state, {
    version: 3,
    status: "completed",
    attempts: 2,
    payload: {
      solution_revealed: true,
      unknown: "zachowaj",
      completion_method: "solution_shown",
    },
  });
  assert.equal(Object.prototype.hasOwnProperty.call(state, "score"), false);
});


test("ręczne ukończenie zachowuje istniejący score", () => {
  const state = createManualCompletionProgressState(activity, {
    status: "in_progress",
    score: 0,
    attempts: 1,
  }, {
    completionMethod: "self_marked",
  });

  assert.equal(state.score, 0);
  assert.equal(state.payload.completion_method, "self_marked");
});


test("completion_method jest write-once po ukończeniu", () => {
  const state = createManualCompletionProgressState(activity, {
    status: "completed",
    attempts: 3,
    payload: { completion_method: "solution_shown" },
  }, {
    completionMethod: "self_marked",
    payloadPatch: { completion_method: "self_marked" },
    removePayloadKeys: ["completion_method"],
  });

  assert.equal(state.payload.completion_method, "solution_shown");
  assert.equal(state.attempts, 3);
});


test("legacy completed z score 1 otrzymuje checked dopiero podczas budowania nowego stanu", () => {
  const legacyState = {
    status: "completed",
    score: 1,
    attempts: 2,
    payload: { source_code: "print('stary')" },
  };
  assert.equal(legacyState.payload.completion_method, undefined);

  const state = createCodeRunProgressState(
    activity,
    legacyState,
    "print('nowy')",
  );

  assert.equal(legacyState.payload.completion_method, undefined);
  assert.equal(state.payload.completion_method, "checked");
});


test("Run zachowuje status, attempts, opcjonalny score i metadane, ale usuwa last_result", () => {
  const previousState = {
    status: "completed",
    score: 1,
    attempts: 5,
    payload: {
      source_code: "stary",
      last_result: "correct",
      completion_method: "self_marked",
      solution_revealed: true,
      unknown: "zachowaj",
    },
  };
  const snapshot = structuredClone(previousState);

  const state = createCodeRunProgressState(activity, previousState, "nowy");

  assert.deepEqual(state, {
    version: 3,
    status: "completed",
    score: 1,
    attempts: 5,
    payload: {
      source_code: "nowy",
      completion_method: "self_marked",
      solution_revealed: true,
      unknown: "zachowaj",
    },
  });
  assert.deepEqual(previousState, snapshot);
});


test("pierwszy Run nie syntetyzuje score ani completion_method", () => {
  const state = createCodeRunProgressState(activity, null, "print('start')");

  assert.deepEqual(state, {
    version: 3,
    status: "in_progress",
    attempts: 0,
    payload: { source_code: "print('start')" },
  });
  assert.equal(Object.prototype.hasOwnProperty.call(state, "score"), false);
});


test("score 1 bez statusu completed nie oznacza ukończenia ani metody checked", () => {
  const state = createCodeRunProgressState(activity, {
    status: "in_progress",
    score: 1,
    attempts: 1,
    payload: {},
  }, "pass");

  assert.equal(state.status, "in_progress");
  assert.equal(state.score, 1);
  assert.equal(state.payload.completion_method, undefined);
});


test("niepoprawna ręczna metoda ukończenia jest odrzucana", () => {
  assert.throws(
    () => createManualCompletionProgressState(activity, null, {
      completionMethod: "checked",
    }),
    /solution_shown albo self_marked/,
  );
});
