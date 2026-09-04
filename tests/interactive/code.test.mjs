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
    correct: "Program wypisał wszystkie znaki w oczekiwanej kolejności.",
    incorrect: "Wynik powinien zawierać znaki a, b i c.",
  },
  solution: {
    code: "for znak in \"abc\":\n    print(znak)\n",
    discussion: "Pętla przechodzi po kolejnych znakach łańcucha, a print wypisuje każdy z nich w osobnym wierszu.",
    alternatives: [
      {
        label: "Indeksy łańcucha",
        code: "tekst = \"abc\"\nfor indeks in range(len(tekst)):\n    print(tekst[indeks])\n",
        discussion: "Indeksy prowadzą do tych samych znaków, choć bezpośrednia iteracja jest tu prostsza.",
      },
    ],
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
    this.focused = false;
    this.hidden = false;
    this.listeners = new Map();
    this.selectionEnd = 0;
    this.selectionStart = 0;
    this.textContent = "";
    this.value = "";
  }

  addEventListener(type, listener) {
    const listeners = this.listeners.get(type) ?? [];
    listeners.push(listener);
    this.listeners.set(type, listeners);
  }

  append(...children) {
    this.children.push(...children);
  }

  replaceChildren(...children) {
    this.children = [...children];
  }

  focus() {
    this.focused = true;
  }

  getAttribute(name) {
    return this.attributes.get(name) ?? null;
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
    const element = new FakeElement(tagName);
    element.ownerDocument = fakeDocument;
    return element;
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
  const resetCalls = [];
  return {
    get saveCount() {
      return saveCount;
    },
    get state() {
      return state;
    },
    get resetCalls() {
      return resetCalls;
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
    async reset(activityIds = null) {
      resetCalls.push(activityIds);
      if (activityIds === null || activityIds.includes(activity.activity_id)) {
        state = null;
      }
    },
  };
}


async function renderCodeForTest({
  definition = activity,
  initialState = null,
  stdout = "",
  stderr = "",
  runtime: suppliedRuntime = null,
  store: suppliedStore = null,
} = {}) {
  const store = suppliedStore ?? createMemoryStore(initialState);
  const runtime = suppliedRuntime ?? {
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
    restoreCodeButton: button("Przywróć kod początkowy"),
    checkButton: button("Sprawdź"),
    stateActionButton: findElement(
      section,
      (element) => element.className.split(" ").includes(
        "interactive-activity__state-action",
      ),
    ),
    solutionButton: button("Pokaż"),
    discussionButton: button("Omów"),
    status: findElement(
      section,
      (element) => element.className === "interactive-activity__runtime-status",
    ),
    stdout: findElement(
      section,
      (element) => element.tagName === "pre"
        && element.attributes.get("aria-labelledby")?.endsWith("stdout-label"),
    ),
    stderr: findElement(
      section,
      (element) => element.tagName === "pre"
        && element.attributes.get("aria-labelledby")?.endsWith("stderr-label"),
    ),
    feedback: findElement(
      section,
      (element) => element.className.split(" ").includes(
        "interactive-activity__message",
      ),
    ),
    summary: findElement(
      section,
      (element) => element.className === "interactive-activity__meta",
    ),
    progress: findElement(
      section,
      (element) => element.className.split(" ").includes(
        "interactive-activity__progress",
      ),
    ),
    solutionPanel: findElement(
      section,
      (element) => element.dataset.helpPanel === "solution",
    ),
    discussionPanel: findElement(
      section,
      (element) => element.dataset.helpPanel === "discussion",
    ),
    runtime,
  };
}


function assertIdleControls(rendered) {
  assert.equal(rendered.editor.disabled, false);
  assert.equal(rendered.runButton.disabled, false);
  assert.equal(rendered.stopButton.disabled, true);
  assert.equal(rendered.resetButton.disabled, false);
  assert.equal(rendered.checkButton.disabled, false);
  assert.equal(rendered.stateActionButton.disabled, false);
}


async function click(element) {
  for (const listener of element.listeners.get("click") ?? []) {
    await listener();
  }
}


function emit(element, type, event = {}) {
  return (element.listeners.get(type) ?? []).map((listener) => listener(event));
}


test("stan kontrolek po sprawdzeniu pozostaje interaktywny", () => {
  assert.deepEqual(
    deriveCodeControlState({
      preparing: false,
      running: false,
      checking: false,
      executionIsCurrent: true,
      workerAvailable: true,
      activityCanRestart: true,
    }),
    {
      editorDisabled: false,
      runDisabled: false,
      stopDisabled: true,
      resetDisabled: false,
      checkDisabled: false,
      restartActivityDisabled: false,
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

  emit(rendered.editor, "keydown", {
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

  emit(rendered.editor, "keydown", {
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
  assert.equal(prompt.children[1].tagName, "span");
  assert.equal(prompt.children[1].textContent, ` ${activity.prompt}`);
  const elements = allElements(rendered.section);
  assert.ok(
    elements.indexOf(prompt) < elements.indexOf(rendered.editor),
  );
  assert.match(
    rendered.editor.attributes.get("aria-describedby"),
    new RegExp(prompt.id),
  );
});


test("rozwiązanie jest inline, reset techniczny osobno, a akcja stanu zachowuje tożsamość w nagłówku", async () => {
  const rendered = await renderCodeForTest();
  const header = findElement(
    rendered.section,
    (element) => element.className === "interactive-activity__header",
  );
  const headerState = findElement(
    header,
    (element) => element.className === "interactive-activity__header-state",
  );
  const executionActions = findElement(
    rendered.section,
    (element) => element.className === "interactive-activity__actions",
  );
  const solutionActions = findElement(
    rendered.section,
    (element) => element.className === "interactive-activity__solution-actions",
  );
  const technicalActions = findElement(
    rendered.section,
    (element) => element.className === "interactive-activity__technical-actions",
  );

  assert.ok(header);
  assert.ok(headerState);
  assert.strictEqual(headerState.children[0], rendered.stateActionButton);
  assert.strictEqual(headerState.children[1], rendered.progress);
  assert.equal(
    allElements(rendered.section).filter(
      (element) => element.className.split(" ").includes(
        "interactive-activity__state-action",
      ),
    ).length,
    1,
  );
  assert.strictEqual(executionActions.children.at(-1), solutionActions);
  assert.deepEqual(
    solutionActions.children.map((element) => element.textContent),
    ["Rozwiązanie:", "Pokaż", "Omów"],
  );
  assert.equal(
    rendered.solutionButton.attributes.get("aria-label"),
    "Pokaż rozwiązanie",
  );
  assert.equal(
    rendered.discussionButton.attributes.get("aria-label"),
    "Omów rozwiązanie",
  );
  assert.deepEqual(
    technicalActions.children,
    [rendered.restoreCodeButton, rendered.resetButton],
  );
  assert.equal(rendered.restoreCodeButton.type, "button");
  assert.equal(rendered.restoreCodeButton.disabled, true);
  assert.equal(rendered.section.textContent.includes("Pomoc"), false);
  assert.equal(
    rendered.section.textContent.includes("Pokaż rozwiązanie"),
    false,
  );
  assert.equal(
    rendered.section.textContent.includes("Omów rozwiązanie"),
    false,
  );
  assert.equal(rendered.stateActionButton.textContent, "Oznacz jako wykonane");

  const stateActionIdentity = rendered.stateActionButton;
  await click(stateActionIdentity);

  assert.strictEqual(
    findElement(
      rendered.section,
      (element) => element.className.split(" ").includes(
        "interactive-activity__state-action",
      ),
    ),
    stateActionIdentity,
  );
  assert.equal(stateActionIdentity.textContent, "Zacznij od nowa");
  assert.equal(stateActionIdentity.focused, true);
  assert.equal(rendered.restoreCodeButton.disabled, true);
});


test("Escape w textarea przenosi fokus do pierwszego dostępnego przycisku", async () => {
  const rendered = await renderCodeForTest();
  let defaultPrevented = false;

  emit(rendered.editor, "keydown", {
    key: "Escape",
    preventDefault() {
      defaultPrevented = true;
    },
  });

  assert.equal(defaultPrevented, true);
  assert.equal(rendered.runButton.focused, true);
  assert.equal(rendered.stopButton.focused, false);
  assert.equal(rendered.resetButton.focused, false);
  assert.equal(rendered.checkButton.focused, false);
});


test("Resetuj interpreter jest disabled bez Workera, także po odtworzeniu completed", async () => {
  let resetCount = 0;
  const runtime = {
    async run() {
      return { stdout: "", stderr: "" };
    },
    stop() {},
    reset() {
      resetCount += 1;
    },
  };
  const rendered = await renderCodeForTest({
    initialState: {
      activity_id: activity.activity_id,
      status: "completed",
      score: 1,
      attempts: 2,
      payload: { source_code: "print('ukończono')" },
    },
    runtime,
  });

  assert.equal(rendered.progress.textContent, "✓ Wykonano");
  assert.equal(rendered.resetButton.disabled, true);
  assert.equal(rendered.stateActionButton.disabled, false);

  await click(rendered.resetButton);
  assert.equal(resetCount, 0);
});


test("odrzucony Run jako busy nie przypisuje rendererowi cudzego Workera", async () => {
  const runtime = {
    async run() {
      throw Object.assign(new Error("busy"), { code: "busy" });
    },
    stop() {},
    reset() {},
  };
  const rendered = await renderCodeForTest({ runtime });

  await click(rendered.runButton);

  assert.equal(rendered.resetButton.disabled, true);
  assert.equal(rendered.runButton.disabled, false);
});


test("pierwszy Run rozpoczyna aktywność bez zaliczenia", () => {
  assert.deepEqual(
    createCodeRunProgressState(activity, null, "print('a')"),
    {
      version: 1,
      status: "in_progress",
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
        completion_method: "checked",
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
        completion_method: "checked",
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
        completion_method: "checked",
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
  const feedback = findElement(
    rendered.section,
    (element) => element.className.includes(
      "interactive-activity__message--incorrect",
    ),
  );
  const resultLabel = findElement(
    feedback,
    (element) => element.className === "interactive-activity__message-result",
  );
  const explanation = findElement(
    feedback,
    (element) => element.className === "interactive-activity__message-explanation",
  );
  const summary = findElement(
    rendered.section,
    (element) => element.className === "interactive-activity__meta",
  );
  assert.equal(resultLabel.textContent, "! Niepoprawnie");
  assert.equal(explanation.textContent, activity.feedback.incorrect);
  assert.equal(summary.textContent, "Próby: 1");
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
  assert.equal(rendered.store.state.payload.completion_method, "checked");
  const feedback = findElement(
    rendered.section,
    (element) => element.className.includes(
      "interactive-activity__message--correct",
    ),
  );
  const resultLabel = findElement(
    feedback,
    (element) => element.className === "interactive-activity__message-result",
  );
  const explanation = findElement(
    feedback,
    (element) => element.className === "interactive-activity__message-explanation",
  );
  const summary = findElement(
    rendered.section,
    (element) => element.className === "interactive-activity__meta",
  );
  assert.equal(resultLabel.textContent, "✓ Poprawnie");
  assert.equal(explanation.textContent, activity.feedback.correct);
  assert.equal(summary.textContent, "Próby: 1");
  assertIdleControls(rendered);
});


test("Pokaż rozwiązanie nie zmienia kodu, nie uruchamia runtime i kończy bez próby ani score", async () => {
  let runCount = 0;
  const runtime = {
    async run() {
      runCount += 1;
      return { stdout: "", stderr: "" };
    },
    stop() {},
    reset() {},
  };
  const rendered = await renderCodeForTest({ runtime });
  rendered.editor.value = "print('moja próba')";
  emit(rendered.editor, "input");

  await click(rendered.solutionButton);

  assert.equal(rendered.solutionPanel.hidden, false);
  assert.equal(rendered.discussionPanel.hidden, true);
  assert.equal(
    findElement(
      rendered.solutionPanel,
      (element) => element.tagName === "code",
    ).textContent,
    activity.solution.code,
  );
  assert.equal(rendered.editor.value, "print('moja próba')");
  assert.equal(runCount, 0);
  assert.equal(rendered.store.state.status, "completed");
  assert.equal(rendered.store.state.attempts, 0);
  assert.equal("score" in rendered.store.state, false);
  assert.equal(
    rendered.store.state.payload.completion_method,
    "solution_shown",
  );
  assert.equal(rendered.store.state.payload.solution_revealed, true);
  assert.equal(rendered.store.state.payload.source_code, "print('moja próba')");
  assert.equal(rendered.progress.textContent, "✓ Wykonano");
  assert.equal(rendered.stateActionButton.textContent, "Zacznij od nowa");
});


test("błąd zapisu po Pokaż rozwiązanie nie ukrywa treści ani nie pokazuje fałszywego completed", async (t) => {
  const warning = t.mock.method(console, "warn", () => {});
  let runCount = 0;
  const store = createMemoryStore();
  store.save = async () => {
    throw new Error("save failed");
  };
  const runtime = {
    async run() {
      runCount += 1;
      return { stdout: "", stderr: "" };
    },
    stop() {},
    reset() {},
  };
  const rendered = await renderCodeForTest({ store, runtime });

  await click(rendered.solutionButton);

  assert.equal(rendered.solutionPanel.hidden, false);
  assert.equal(rendered.solutionButton.attributes.get("aria-expanded"), "true");
  assert.equal(rendered.editor.value, activity.starter_code);
  assert.equal(runCount, 0);
  assert.equal(store.state, null);
  assert.equal(rendered.progress.textContent, "○ Do wykonania");
  assert.equal(
    rendered.stateActionButton.textContent,
    "Oznacz jako wykonane",
  );
  assert.equal(rendered.feedback.hidden, false);
  assert.equal(
    rendered.feedback.textContent,
    "Błąd techniczny: nie udało się zapisać postępu.",
  );
  assert.equal(warning.mock.callCount(), 1);
});


test("niezapisane ujawnienie nie trafia do późniejszego Run", async (t) => {
  const warning = t.mock.method(console, "warn", () => {});
  const store = createMemoryStore();
  const successfulSave = store.save.bind(store);
  let rejectNextSave = true;
  store.save = async (...args) => {
    if (rejectNextSave) {
      rejectNextSave = false;
      throw new Error("save failed");
    }
    return successfulSave(...args);
  };
  const rendered = await renderCodeForTest({ store });

  await click(rendered.solutionButton);
  await click(rendered.runButton);

  assert.equal(rendered.solutionPanel.hidden, false);
  assert.equal(store.state.status, "in_progress");
  assert.equal(store.state.payload.solution_revealed, undefined);
  assert.equal(store.state.payload.completion_method, undefined);
  assert.equal(warning.mock.callCount(), 1);

  const reloaded = await renderCodeForTest({ store });
  assert.equal(reloaded.solutionPanel.hidden, true);
});


test("ręczne ukończenie po zmianie kodu usuwa feedback starego Check", async () => {
  const store = createMemoryStore({
    activity_id: activity.activity_id,
    version: activity.version,
    status: "in_progress",
    score: 0,
    attempts: 1,
    payload: {
      source_code: "print('stary kod')",
      last_result: "incorrect",
      unknown_future_field: "zachowaj",
    },
  });
  const rendered = await renderCodeForTest({ store });
  rendered.editor.value = "print('nowy kod')";
  emit(rendered.editor, "input");

  await click(rendered.stateActionButton);

  assert.equal(store.state.payload.source_code, "print('nowy kod')");
  assert.equal(store.state.payload.last_result, undefined);
  assert.equal(store.state.payload.unknown_future_field, "zachowaj");
  assert.equal(store.state.payload.completion_method, "self_marked");
});


test("Omów rozwiązanie ujawnia oba panele i zapisuje obie flagi", async () => {
  const rendered = await renderCodeForTest();

  await click(rendered.discussionButton);

  assert.equal(rendered.solutionPanel.hidden, false);
  assert.equal(rendered.discussionPanel.hidden, false);
  assert.equal(rendered.store.state.status, "completed");
  assert.equal(rendered.store.state.attempts, 0);
  assert.equal("score" in rendered.store.state, false);
  assert.equal(
    rendered.store.state.payload.completion_method,
    "solution_shown",
  );
  assert.equal(rendered.store.state.payload.solution_revealed, true);
  assert.equal(rendered.store.state.payload.discussion_revealed, true);
});


test("self_marked pozostaje metodą ukończenia po późniejszym poprawnym Check", async () => {
  const rendered = await renderCodeForTest({ stdout: "a\nb\nc\n" });

  await click(rendered.stateActionButton);
  assert.equal(rendered.store.state.status, "completed");
  assert.equal(rendered.store.state.attempts, 0);
  assert.equal("score" in rendered.store.state, false);
  assert.equal(
    rendered.store.state.payload.completion_method,
    "self_marked",
  );

  await click(rendered.runButton);
  await click(rendered.checkButton);

  assert.equal(rendered.store.state.status, "completed");
  assert.equal(rendered.store.state.score, 1);
  assert.equal(rendered.store.state.attempts, 1);
  assert.equal(
    rendered.store.state.payload.completion_method,
    "self_marked",
  );
});


test("checked pozostaje metodą ukończenia po późniejszym pokazaniu rozwiązania", async () => {
  const rendered = await renderCodeForTest({ stdout: "a\nb\nc\n" });

  await click(rendered.runButton);
  await click(rendered.checkButton);
  await click(rendered.solutionButton);

  assert.equal(rendered.store.state.status, "completed");
  assert.equal(rendered.store.state.score, 1);
  assert.equal(rendered.store.state.attempts, 1);
  assert.equal(rendered.store.state.payload.completion_method, "checked");
  assert.equal(rendered.store.state.payload.solution_revealed, true);
  assert.equal(rendered.solutionPanel.hidden, false);
});


test("reload odtwarza ujawnione rozwiązanie i omówienie bez nowego zapisu", async () => {
  const initialState = {
    activity_id: activity.activity_id,
    version: activity.version,
    status: "completed",
    attempts: 2,
    payload: {
      source_code: "print('własny kod')",
      completion_method: "solution_shown",
      solution_revealed: true,
      discussion_revealed: true,
      custom_future_field: "zachowaj",
    },
  };
  const store = createMemoryStore(initialState);

  const rendered = await renderCodeForTest({ store });

  assert.equal(rendered.solutionPanel.hidden, false);
  assert.equal(rendered.discussionPanel.hidden, false);
  assert.equal(rendered.editor.value, "print('własny kod')");
  assert.equal(rendered.solutionButton.attributes.get("aria-expanded"), "true");
  assert.equal(rendered.discussionButton.attributes.get("aria-expanded"), "true");
  assert.equal(store.saveCount, 0);
});


test("historyczne completed z score 1 nie zapisuje migracji przy renderze i utrwala checked przy kolejnym zapisie", async () => {
  const store = createMemoryStore({
    activity_id: activity.activity_id,
    version: activity.version,
    status: "completed",
    score: 1,
    attempts: 2,
    payload: { source_code: "print('historyczny kod')" },
  });
  const rendered = await renderCodeForTest({ store });

  assert.equal(rendered.progress.textContent, "✓ Wykonano");
  assert.equal(store.saveCount, 0);
  assert.equal(store.state.payload.completion_method, undefined);

  await click(rendered.solutionButton);

  assert.equal(store.saveCount, 1);
  assert.equal(store.state.payload.completion_method, "checked");
  assert.equal(store.state.payload.solution_revealed, true);
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
  const feedback = findElement(
    rendered.section,
    (element) => element.className.includes(
      "interactive-activity__message--error",
    ),
  );
  assert.equal(
    feedback.textContent,
    "Błąd techniczny: nie można sprawdzić rozwiązania z powodu błędu konfiguracji aktywności.",
  );
  assert.equal(
    feedback.className.includes("interactive-activity__message--incorrect"),
    false,
  );
  assert.equal(
    findElement(
      feedback,
      (element) => element.className === "interactive-activity__message-result",
    ),
    undefined,
  );
  assert.equal(errorLog.mock.callCount(), 1);
  assert.ok(errorLog.mock.calls[0].arguments[1] instanceof Error);
  assertIdleControls(rendered);
});


test("Przywróć kod początkowy czyści lokalną edycję bez zbędnego resetu", async () => {
  let runtimeResetCount = 0;
  const runtime = {
    async run() {
      return { stdout: "", stderr: "" };
    },
    stop() {},
    reset() {
      runtimeResetCount += 1;
    },
  };
  const rendered = await renderCodeForTest({ runtime });

  assert.equal(rendered.restoreCodeButton.disabled, true);
  rendered.editor.value = "print('lokalna zmiana')";
  emit(rendered.editor, "input");
  assert.equal(rendered.restoreCodeButton.disabled, false);

  await click(rendered.restoreCodeButton);

  assert.equal(rendered.editor.value, activity.starter_code);
  assert.equal(rendered.editor.focused, true);
  assert.equal(rendered.stdout.textContent, "");
  assert.equal(rendered.stderr.textContent, "");
  assert.equal(rendered.feedback.hidden, true);
  assert.equal(rendered.checkButton.disabled, true);
  assert.equal(rendered.restoreCodeButton.disabled, true);
  assert.equal(rendered.progress.textContent, "○ Do wykonania");
  assert.equal(rendered.summary.textContent, "Próby: 0");
  assert.equal(rendered.store.state, null);
  assert.equal(rendered.store.saveCount, 0);
  assert.deepEqual(rendered.store.resetCalls, []);
  assert.equal(runtimeResetCount, 0);
});


test("Przywróć kod początkowy zachowuje historię stanu in_progress", async () => {
  let runtimeResetCount = 0;
  const initialState = {
    activity_id: activity.activity_id,
    version: activity.version,
    status: "in_progress",
    score: 0,
    attempts: 2,
    payload: {
      source_code: "print('poprzednia próba')",
      last_result: "incorrect",
      future_metadata: "zachowaj",
    },
  };
  const runtime = {
    async run() {
      return { stdout: "a\nb\n", stderr: "ostrzeżenie\n" };
    },
    stop() {},
    reset() {
      runtimeResetCount += 1;
    },
  };
  const rendered = await renderCodeForTest({ initialState, runtime });

  await click(rendered.runButton);
  await click(rendered.checkButton);
  assert.equal(rendered.store.state.status, "in_progress");
  assert.equal(rendered.store.state.score, 0);
  assert.equal(rendered.store.state.attempts, 3);
  assert.equal(rendered.store.state.payload.last_result, "incorrect");
  assert.equal(rendered.restoreCodeButton.disabled, false);

  await click(rendered.restoreCodeButton);

  assert.deepEqual(rendered.store.resetCalls, []);
  assert.equal(rendered.store.saveCount, 3);
  assert.equal(rendered.store.state.status, "in_progress");
  assert.equal(rendered.store.state.score, 0);
  assert.equal(rendered.store.state.attempts, 3);
  assert.equal(
    rendered.store.state.payload.source_code,
    activity.starter_code,
  );
  assert.equal(
    Object.hasOwn(rendered.store.state.payload, "last_result"),
    false,
  );
  assert.equal(rendered.store.state.payload.future_metadata, "zachowaj");
  assert.equal(
    Object.hasOwn(rendered.store.state.payload, "completion_method"),
    false,
  );
  assert.equal(runtimeResetCount, 1);
  assert.equal(rendered.editor.value, activity.starter_code);
  assert.equal(rendered.stdout.textContent, "");
  assert.equal(rendered.stderr.textContent, "");
  assert.equal(rendered.feedback.hidden, true);
  assert.equal(rendered.checkButton.disabled, true);
  assert.equal(rendered.resetButton.disabled, true);
  assert.equal(rendered.restoreCodeButton.disabled, true);
  assert.equal(rendered.progress.textContent, "○ Do wykonania");
  assert.equal(rendered.summary.textContent, "Próby: 3");
});


test("Przywróć kod początkowy jest niedostępne po completed", async () => {
  let runtimeResetCount = 0;
  const initialState = {
    activity_id: activity.activity_id,
    version: activity.version,
    status: "completed",
    score: 1,
    attempts: 2,
    payload: {
      source_code: "print('ukończono')",
      completion_method: "checked",
    },
  };
  const store = createMemoryStore(initialState);
  const runtime = {
    async run() {
      return { stdout: "", stderr: "" };
    },
    stop() {},
    reset() {
      runtimeResetCount += 1;
    },
  };
  const rendered = await renderCodeForTest({ store, runtime });

  assert.equal(rendered.restoreCodeButton.disabled, true);
  rendered.editor.value = "print('zmiana po ukończeniu')";
  emit(rendered.editor, "input");
  assert.equal(rendered.restoreCodeButton.disabled, true);

  await click(rendered.restoreCodeButton);

  assert.equal(rendered.editor.value, "print('zmiana po ukończeniu')");
  assert.deepEqual(store.state, initialState);
  assert.deepEqual(store.resetCalls, []);
  assert.equal(runtimeResetCount, 0);
  assert.equal(rendered.stateActionButton.textContent, "Zacznij od nowa");
});


test("Przywróć kod początkowy przerywa aktywny Run w stanie pending", async () => {
  let rejectRun;
  let markRunStarted;
  const events = [];
  const runStarted = new Promise((resolve) => {
    markRunStarted = resolve;
  });
  const runtime = {
    run(sourceCode) {
      events.push(["runtime.run", sourceCode]);
      markRunStarted();
      return new Promise((resolve, reject) => {
        rejectRun = reject;
      });
    },
    stop() {},
    reset() {
      events.push(["runtime.reset"]);
      const reject = rejectRun;
      rejectRun = null;
      reject?.(Object.assign(new Error("reset"), { code: "reset" }));
    },
  };
  const store = createMemoryStore();
  const originalReset = store.reset.bind(store);
  store.reset = async (activityIds) => {
    events.push(["store.reset", activityIds]);
    await originalReset(activityIds);
  };
  const rendered = await renderCodeForTest({ runtime, store });
  rendered.editor.value = "while True:\n    pass\n";
  emit(rendered.editor, "input");

  const pendingRun = click(rendered.runButton);
  await runStarted;
  assert.equal(rendered.restoreCodeButton.disabled, false);

  await click(rendered.restoreCodeButton);
  await pendingRun;

  assert.deepEqual(events, [
    ["runtime.run", "while True:\n    pass\n"],
    ["runtime.reset"],
  ]);
  assert.deepEqual(store.resetCalls, []);
  assert.equal(store.state.status, "in_progress");
  assert.equal(store.state.attempts, 0);
  assert.equal(store.state.payload.source_code, activity.starter_code);
  assert.equal(Object.hasOwn(store.state.payload, "last_result"), false);
  assert.equal(rendered.editor.value, activity.starter_code);
  assert.equal(rendered.stdout.textContent, "");
  assert.equal(rendered.stderr.textContent, "");
  assert.equal(rendered.restoreCodeButton.disabled, true);
  assert.equal(rendered.progress.textContent, "○ Do wykonania");
});


test("stan pending po lokalnej zmianie Oznacz jako wykonane zapisuje self_marked bez resetu", async () => {
  let runtimeResetCount = 0;
  const runtime = {
    async run() {
      return { stdout: "", stderr: "" };
    },
    stop() {},
    reset() {
      runtimeResetCount += 1;
    },
  };
  const rendered = await renderCodeForTest({ runtime });
  assert.equal(rendered.resetButton.disabled, true);
  rendered.editor.value = "print('lokalna zmiana')";
  emit(rendered.editor, "input");

  assert.equal(rendered.stateActionButton.disabled, false);
  assert.equal(rendered.stateActionButton.textContent, "Oznacz jako wykonane");
  await click(rendered.stateActionButton);

  assert.equal(runtimeResetCount, 0);
  assert.deepEqual(rendered.store.resetCalls, []);
  assert.equal(rendered.store.state.status, "completed");
  assert.equal(rendered.store.state.attempts, 0);
  assert.equal(rendered.store.state.payload.completion_method, "self_marked");
  assert.equal(
    rendered.store.state.payload.source_code,
    "print('lokalna zmiana')",
  );
  assert.equal(rendered.editor.value, "print('lokalna zmiana')");
  assert.equal(rendered.summary.textContent, "Próby: 0");
  assert.equal(rendered.progress.textContent, "✓ Wykonano");
  assert.equal(rendered.stateActionButton.textContent, "Zacznij od nowa");
  assert.equal(rendered.resetButton.disabled, true);
  assert.equal(rendered.stateActionButton.disabled, false);
});


test("Zacznij od nowa usuwa completed i po reloadzie odtwarza stan początkowy", async () => {
  const completedState = {
    activity_id: activity.activity_id,
    version: activity.version,
    status: "completed",
    score: 1,
    attempts: 4,
    payload: {
      source_code: "print('zmieniony kod')",
      last_result: "correct",
      completion_method: "checked",
      solution_revealed: true,
      discussion_revealed: true,
    },
  };
  const store = createMemoryStore(completedState);
  const rendered = await renderCodeForTest({
    store,
    stdout: "a\nb\nc\n",
  });

  await click(rendered.stateActionButton);

  assert.deepEqual(store.resetCalls, [[activity.activity_id]]);
  assert.equal(store.state, null);
  assert.equal(rendered.progress.textContent, "○ Do wykonania");
  assert.equal(rendered.summary.textContent, "Próby: 0");
  assert.equal(rendered.editor.value, activity.starter_code);
  assert.equal(rendered.stdout.textContent, "");
  assert.equal(rendered.stderr.textContent, "");
  assert.equal(rendered.feedback.hidden, true);
  assert.equal(rendered.solutionPanel.hidden, true);
  assert.equal(rendered.discussionPanel.hidden, true);
  assert.equal(rendered.resetButton.disabled, true);
  assert.equal(rendered.editor.focused, true);

  const reloaded = await renderCodeForTest({ store });
  assert.equal(reloaded.progress.textContent, "○ Do wykonania");
  assert.equal(reloaded.summary.textContent, "Próby: 0");
  assert.equal(reloaded.editor.value, activity.starter_code);
  assert.equal(reloaded.solutionPanel.hidden, true);
  assert.equal(reloaded.discussionPanel.hidden, true);
  assert.equal(reloaded.resetButton.disabled, true);
  assert.equal(reloaded.stateActionButton.disabled, false);

  await click(rendered.runButton);
  await click(rendered.checkButton);
  assert.equal(store.state.status, "completed");
  assert.equal(store.state.attempts, 1);
});


test("Zacznij od nowa przerywa aktywny while True przed usunięciem postępu", async () => {
  const events = [];
  let rejectRun;
  let markRunStarted;
  const runStarted = new Promise((resolve) => {
    markRunStarted = resolve;
  });
  const runtime = {
    run(sourceCode) {
      events.push(["runtime.run", sourceCode]);
      markRunStarted();
      return new Promise((resolve, reject) => {
        rejectRun = reject;
      });
    },
    stop() {},
    reset() {
      events.push(["runtime.reset"]);
      if (rejectRun) {
        const reject = rejectRun;
        rejectRun = null;
        reject(Object.assign(new Error("reset"), { code: "reset" }));
      }
    },
  };
  const store = createMemoryStore({
    activity_id: activity.activity_id,
    version: activity.version,
    status: "completed",
    score: 1,
    attempts: 1,
    payload: {
      source_code: "while True:\n    pass\n",
      completion_method: "checked",
    },
  });
  const originalReset = store.reset.bind(store);
  store.reset = async (activityIds) => {
    events.push(["store.reset", activityIds]);
    await originalReset(activityIds);
  };
  const rendered = await renderCodeForTest({ runtime, store });
  assert.equal(rendered.stateActionButton.textContent, "Zacznij od nowa");

  const pendingRun = click(rendered.runButton);
  await runStarted;
  assert.equal(rendered.stopButton.disabled, false);
  assert.equal(rendered.resetButton.disabled, false);
  assert.equal(rendered.stateActionButton.disabled, false);

  await click(rendered.stateActionButton);
  await pendingRun;

  assert.deepEqual(events, [
    ["runtime.run", "while True:\n    pass\n"],
    ["runtime.reset"],
    ["store.reset", [activity.activity_id]],
  ]);
  assert.equal(store.state, null);
  assert.equal(rendered.editor.value, activity.starter_code);
  assert.equal(rendered.progress.textContent, "○ Do wykonania");
  assert.equal(rendered.summary.textContent, "Próby: 0");
  assert.equal(rendered.resetButton.disabled, true);
});


test("Resetuj interpreter zachowuje kod i completed, po czym staje się disabled", async () => {
  let runtimeResetCount = 0;
  const runtime = {
    async run() {
      return { stdout: "a\nb\nc\n", stderr: "" };
    },
    stop() {},
    reset() {
      runtimeResetCount += 1;
    },
  };
  const store = createMemoryStore({
    activity_id: activity.activity_id,
    status: "completed",
    score: 1,
    attempts: 2,
    payload: { source_code: "print('zachowaj')" },
  });
  const rendered = await renderCodeForTest({ runtime, store });

  await click(rendered.runButton);
  const codeBeforeReset = rendered.editor.value;
  const stateBeforeReset = structuredClone(store.state);
  assert.equal(rendered.resetButton.disabled, false);

  await click(rendered.resetButton);

  assert.equal(runtimeResetCount, 1);
  assert.equal(rendered.editor.value, codeBeforeReset);
  assert.deepEqual(store.state, stateBeforeReset);
  assert.equal(rendered.progress.textContent, "✓ Wykonano");
  assert.deepEqual(store.resetCalls, []);
  assert.equal(rendered.resetButton.disabled, true);
  assert.equal(rendered.stateActionButton.disabled, false);
});


test("błąd store.reset zachowuje kod i completed oraz pokazuje błąd techniczny", async (t) => {
  const warning = t.mock.method(console, "warn", () => {});
  const store = createMemoryStore({
    activity_id: activity.activity_id,
    status: "completed",
    score: 1,
    attempts: 2,
    payload: { source_code: "print('zachowaj')" },
  });
  store.reset = async () => {
    throw new Error("reset failed");
  };
  const rendered = await renderCodeForTest({ store });

  await click(rendered.stateActionButton);

  assert.equal(rendered.editor.value, "print('zachowaj')");
  assert.equal(rendered.progress.textContent, "✓ Wykonano");
  assert.equal(rendered.summary.textContent, "Próby: 2");
  assert.equal(rendered.feedback.hidden, false);
  assert.match(rendered.feedback.textContent, /^Błąd techniczny:/);
  assert.equal(rendered.resetButton.disabled, true);
  assert.equal(rendered.stateActionButton.disabled, false);
  assert.equal(warning.mock.callCount(), 1);
});
