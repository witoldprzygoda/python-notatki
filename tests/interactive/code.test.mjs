import assert from "node:assert/strict";
import test from "node:test";

import {
  applyCodeIndentation,
  checkCodeResult,
  createCodeCheckProgressState,
  createCodeRenderer,
  createCodeRunProgressState,
  deriveCodeControlState,
} from "../../docs/javascripts/interactive/activities/code.js";


const activity = {
  activity_id: "flow-for-code-001",
  version: 1,
  label: "Ćwiczenie: iteracja po łańcuchu",
  prompt: "Wypisz każdy znak w osobnym wierszu.",
  starter_code: "for znak in \"abc\":\n    pass\n",
  checker: {
    type: "stdout_lines_exact",
    expected_lines: ["a", "b", "c"],
  },
  feedback: {
    correct: "Poprawnie.",
    incorrect: "Niepoprawnie.",
  },
};


class FakeElement {
  constructor(tagName) {
    this.tagName = tagName;
    this.attributes = new Map();
    this.children = [];
    this.className = "";
    this.dataset = {};
    this.disabled = false;
    this.hidden = false;
    this.listeners = new Map();
    this.selectionEnd = 0;
    this.selectionStart = 0;
    this.textContent = "";
    this.value = "";
  }

  addEventListener(type, listener) {
    this.listeners.set(type, listener);
  }

  append(...children) {
    this.children.push(...children);
  }

  setAttribute(name, value) {
    this.attributes.set(name, value);
  }

  setSelectionRange(start, end) {
    this.selectionStart = start;
    this.selectionEnd = end;
  }
}


const fakeDocument = {
  createElement(tagName) {
    return new FakeElement(tagName);
  },
};


function allElements(root) {
  return [
    root,
    ...root.children
      .filter((child) => child instanceof FakeElement)
      .flatMap(allElements),
  ];
}


function findElement(root, predicate) {
  return allElements(root).find(predicate);
}


function createMemoryStore(initialState = null) {
  let state = initialState;
  let saveCount = 0;
  return {
    get saveCount() {
      return saveCount;
    },
    get state() {
      return state;
    },
    async get() {
      return state;
    },
    async save(activityId, nextState) {
      saveCount += 1;
      state = {
        activity_id: activityId,
        ...nextState,
      };
      return state;
    },
  };
}


async function renderCodeForTest({
  definition = activity,
  initialState = null,
  stdout = "",
  stderr = "",
} = {}) {
  const store = createMemoryStore(initialState);
  const runtime = {
    async run() {
      return { stdout, stderr };
    },
    stop() {},
    reset() {},
  };
  const renderer = createCodeRenderer({ runtime });
  const section = await renderer({
    activity: definition,
    store,
    document: fakeDocument,
  });
  const editor = findElement(section, (element) => element.tagName === "textarea");
  const button = (label) => findElement(
    section,
    (element) => element.tagName === "button" && element.textContent === label,
  );
  return {
    section,
    store,
    editor,
    runButton: button("Uruchom"),
    stopButton: button("Zatrzymaj"),
    resetButton: button("Resetuj interpreter"),
    checkButton: button("Sprawdź"),
  };
}


function assertIdleControls(rendered) {
  assert.equal(rendered.editor.disabled, false);
  assert.equal(rendered.runButton.disabled, false);
  assert.equal(rendered.stopButton.disabled, true);
  assert.equal(rendered.resetButton.disabled, false);
  assert.equal(rendered.checkButton.disabled, false);
}


async function click(element) {
  await element.listeners.get("click")();
}


test("stan kontrolek po sprawdzeniu pozostaje interaktywny", () => {
  assert.deepEqual(
    deriveCodeControlState({
      preparing: false,
      running: false,
      checking: false,
      executionIsCurrent: true,
    }),
    {
      editorDisabled: false,
      runDisabled: false,
      stopDisabled: true,
      resetDisabled: false,
      checkDisabled: false,
    },
  );
});


test("Tab wstawia cztery spacje i zastępuje zaznaczenie", () => {
  assert.deepEqual(
    applyCodeIndentation("ab", 1, 1),
    {
      value: "a    b",
      selectionStart: 5,
      selectionEnd: 5,
    },
  );
  assert.deepEqual(
    applyCodeIndentation("aXYZb", 1, 4),
    {
      value: "a    b",
      selectionStart: 5,
      selectionEnd: 5,
    },
  );
});


test("Shift+Tab usuwa jedno wcięcie z bieżącej lub zaznaczonych linii", () => {
  assert.deepEqual(
    applyCodeIndentation("    print()", 6, 6, true),
    {
      value: "print()",
      selectionStart: 2,
      selectionEnd: 2,
    },
  );
  assert.deepEqual(
    applyCodeIndentation("    a\n    b\nc", 0, 11, true),
    {
      value: "a\nb\nc",
      selectionStart: 0,
      selectionEnd: 3,
    },
  );
  assert.deepEqual(
    applyCodeIndentation("    a\n    b", 0, 6, true),
    {
      value: "a\n    b",
      selectionStart: 0,
      selectionEnd: 2,
    },
  );
});


test("renderer obsługuje Tab w textarea bez rozbudowanego edytora", async () => {
  const rendered = await renderCodeForTest();
  rendered.editor.value = "ab";
  rendered.editor.selectionStart = 1;
  rendered.editor.selectionEnd = 1;
  let defaultPrevented = false;

  rendered.editor.listeners.get("keydown")({
    key: "Tab",
    shiftKey: false,
    preventDefault() {
      defaultPrevented = true;
    },
  });

  assert.equal(defaultPrevented, true);
  assert.equal(rendered.editor.value, "a    b");
  assert.equal(rendered.editor.selectionStart, 5);
  assert.equal(rendered.editor.selectionEnd, 5);
});


test("Shift+Tab bez wcięcia zachowuje natywną nawigację fokusu", async () => {
  const rendered = await renderCodeForTest();
  rendered.editor.value = "print()";
  rendered.editor.selectionStart = 2;
  rendered.editor.selectionEnd = 2;
  let defaultPrevented = false;

  rendered.editor.listeners.get("keydown")({
    key: "Tab",
    shiftKey: true,
    preventDefault() {
      defaultPrevented = true;
    },
  });

  assert.equal(defaultPrevented, false);
  assert.equal(rendered.editor.value, "print()");
});


test("prompt z YAML jest wyraźnie renderowany przed edytorem", async () => {
  const rendered = await renderCodeForTest();
  const prompt = findElement(
    rendered.section,
    (element) => element.className === "interactive-activity__prompt",
  );

  assert.ok(prompt);
  assert.equal(prompt.children[0].tagName, "strong");
  assert.equal(prompt.children[0].textContent, "Polecenie:");
  assert.equal(prompt.children[1], ` ${activity.prompt}`);
  assert.ok(
    rendered.section.children.indexOf(prompt)
      < rendered.section.children.indexOf(rendered.editor),
  );
});


test("pierwszy Run rozpoczyna aktywność bez zaliczenia", () => {
  assert.deepEqual(
    createCodeRunProgressState(activity, null, "print('a')"),
    {
      version: 1,
      status: "in_progress",
      score: 0,
      attempts: 0,
      payload: {
        source_code: "print('a')",
      },
    },
  );
});


test("Run po ukończeniu zachowuje monotoniczny status i wynik", () => {
  const previousState = {
    status: "completed",
    score: 1,
    attempts: 3,
    payload: {
      source_code: "print('a')",
      last_result: "correct",
    },
  };

  assert.deepEqual(
    createCodeRunProgressState(activity, previousState, "print('nowy kod')"),
    {
      version: 1,
      status: "completed",
      score: 1,
      attempts: 3,
      payload: {
        source_code: "print('nowy kod')",
      },
    },
  );
});


test("błędne sprawdzenie zwiększa attempts bez ukończenia", () => {
  assert.deepEqual(
    createCodeCheckProgressState(activity, null, "pass", false),
    {
      version: 1,
      status: "in_progress",
      score: 0,
      attempts: 1,
      payload: {
        source_code: "pass",
        last_result: "incorrect",
      },
    },
  );
});


test("poprawne sprawdzenie kończy aktywność", () => {
  const previousState = {
    status: "in_progress",
    score: 0,
    attempts: 1,
  };

  assert.deepEqual(
    createCodeCheckProgressState(activity, previousState, "print('ok')", true),
    {
      version: 1,
      status: "completed",
      score: 1,
      attempts: 2,
      payload: {
        source_code: "print('ok')",
        last_result: "correct",
      },
    },
  );
});


test("błędne sprawdzenie po ukończeniu nie cofa statusu ani wyniku", () => {
  const previousState = {
    status: "completed",
    score: 1,
    attempts: 2,
  };

  assert.deepEqual(
    createCodeCheckProgressState(activity, previousState, "pass", false),
    {
      version: 1,
      status: "completed",
      score: 1,
      attempts: 3,
      payload: {
        source_code: "pass",
        last_result: "incorrect",
      },
    },
  );
});


test("checker akceptuje dokładne wiersze LF i CRLF", () => {
  assert.equal(
    checkCodeResult(activity, {
      stdout: "a\nb\nc\n",
      stderr: "",
    }),
    true,
  );
  assert.equal(
    checkCodeResult(activity, {
      stdout: "a\r\nb\r\nc\r\n",
      stderr: "",
    }),
    true,
  );
});


test("checker odrzuca dodatkową linię, spację i stderr", () => {
  assert.equal(
    checkCodeResult(activity, {
      stdout: "a\nb\nc\nd\n",
      stderr: "",
    }),
    false,
  );
  assert.equal(
    checkCodeResult(activity, {
      stdout: "a\nb\nc \n",
      stderr: "",
    }),
    false,
  );
  assert.equal(
    checkCodeResult(activity, {
      stdout: "a\nb\nc\n",
      stderr: "ostrzeżenie\n",
    }),
    false,
  );
});


test("checker odrzuca wykonanie zakończone wyjątkiem", () => {
  assert.equal(
    checkCodeResult(activity, {
      stdout: "a\nb\nc\n",
      stderr: "",
      error: "PythonError",
    }),
    false,
  );
});


test("niepoprawny Check przywraca kontrolki i pozwala na kolejną próbę", async () => {
  const rendered = await renderCodeForTest({
    stdout: "a\nb\n",
  });

  await click(rendered.runButton);
  await click(rendered.checkButton);

  assert.equal(rendered.store.state.status, "in_progress");
  assert.equal(rendered.store.state.score, 0);
  assert.equal(rendered.store.state.attempts, 1);
  assert.equal(rendered.store.state.payload.last_result, "incorrect");
  assert.ok(findElement(
    rendered.section,
    (element) => element.textContent === activity.feedback.incorrect,
  ));
  assertIdleControls(rendered);
});


test("poprawny Check zalicza aktywność bez blokowania edytora", async () => {
  const rendered = await renderCodeForTest({
    stdout: "a\nb\nc\n",
  });

  await click(rendered.runButton);
  await click(rendered.checkButton);

  assert.equal(rendered.store.state.status, "completed");
  assert.equal(rendered.store.state.score, 1);
  assert.equal(rendered.store.state.attempts, 1);
  assert.equal(rendered.store.state.payload.last_result, "correct");
  assert.ok(findElement(
    rendered.section,
    (element) => element.textContent === activity.feedback.correct,
  ));
  assertIdleControls(rendered);
});


test("błąd konfiguracji checkera nie zmienia postępu i odblokowuje UI", async (t) => {
  const errorLog = t.mock.method(console, "error", () => {});
  const definition = {
    ...activity,
    checker: {
      type: "stdout_lines_exact",
    },
  };
  const rendered = await renderCodeForTest({
    definition,
    stdout: "a\nb\nc\n",
  });

  await click(rendered.runButton);
  const stateBeforeCheck = structuredClone(rendered.store.state);
  const savesBeforeCheck = rendered.store.saveCount;
  await click(rendered.checkButton);

  assert.deepEqual(rendered.store.state, stateBeforeCheck);
  assert.equal(rendered.store.saveCount, savesBeforeCheck);
  assert.ok(findElement(
    rendered.section,
    (element) => element.textContent ===
      "Nie można sprawdzić rozwiązania z powodu błędu konfiguracji aktywności.",
  ));
  assert.equal(errorLog.mock.callCount(), 1);
  assert.ok(errorLog.mock.calls[0].arguments[1] instanceof Error);
  assertIdleControls(rendered);
});
