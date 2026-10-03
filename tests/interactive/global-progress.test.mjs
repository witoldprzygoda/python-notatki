import assert from "node:assert/strict";
import test from "node:test";

import { createCodeRenderer } from "../../docs/javascripts/interactive/activities/code.js";
import { renderSingleChoice } from "../../docs/javascripts/interactive/activities/single-choice.js";
import { createGlobalProgressController } from "../../docs/javascripts/interactive/global-progress.js";
import { NotifyingProgressStore } from "../../docs/javascripts/interactive/notifying-progress-store.js";
import {
  createFakeDocument,
  dispatch,
  findElement,
} from "./support/fake-dom.mjs";


class ObservableMemoryStore {
  constructor(states = {}) {
    this.states = new Map(Object.entries(states));
    this.listeners = new Set();
    this.getCalls = [];
  }

  subscribe(listener) {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  async get(activityId) {
    this.getCalls.push(activityId);
    const state = this.states.get(activityId);
    return state ? { ...state } : null;
  }

  set(activityId, state) {
    this.states.set(activityId, { ...state });
    this.emit({ type: "save", activityId });
  }

  reset(activityIds = null) {
    if (activityIds === null) {
      this.states.clear();
    } else {
      for (const activityId of activityIds) {
        this.states.delete(activityId);
      }
    }
    this.emit({ type: "reset", activityIds });
  }

  emit(event) {
    for (const listener of [...this.listeners]) {
      listener(event);
    }
  }
}


class MemoryProgressStore {
  constructor(states = {}) {
    this.states = new Map(Object.entries(states));
  }

  async get(activityId) {
    const state = this.states.get(activityId);
    return state ? { ...state, payload: state.payload && { ...state.payload } } : null;
  }

  async save(activityId, state) {
    const savedState = { activity_id: activityId, ...state };
    this.states.set(activityId, savedState);
    return { ...savedState };
  }

  async getSummary() {
    return { total: this.states.size, completed: 0 };
  }

  async reset(activityIds = null) {
    if (activityIds === null) {
      this.states.clear();
      return;
    }
    for (const activityId of activityIds) {
      this.states.delete(activityId);
    }
  }
}


function manifest(...activityIds) {
  return {
    activities: activityIds.map((activityId) => ({ activity_id: activityId })),
  };
}


test("działa bez document jako bezgłowy centralny model", async () => {
  const store = new ObservableMemoryStore({
    first: { status: "completed" },
  });
  const controller = createGlobalProgressController({
    manifest: manifest("first"),
    store,
  });

  await controller.ready;

  assert.deepEqual(controller.getSnapshot(), { completed: 1, total: 1 });
  assert.equal(controller.getActivityCompletion("first"), true);
  assert.equal("ensureRoot" in controller, false);
});


test("liczy unikalne ID manifestu i wyłącznie dokładny status completed", async () => {
  const store = new ObservableMemoryStore({
    first: { status: "in_progress", score: 1 },
    second: { status: "completed", score: 0 },
    orphan: { status: "completed" },
  });
  const controller = createGlobalProgressController({
    manifest: manifest("first", "second", "first"),
    store,
  });

  await controller.ready;

  assert.deepEqual(controller.getSnapshot(), { completed: 1, total: 2 });
  assert.deepEqual(store.getCalls.sort(), ["first", "second"]);
});


test("po save odczytuje faktyczny stan i aktualizuje cache", async () => {
  const store = new ObservableMemoryStore();
  const controller = createGlobalProgressController({
    manifest: manifest("first", "second"),
    store,
  });
  await controller.ready;

  store.set("first", { status: "completed" });
  await controller.whenIdle();

  assert.deepEqual(controller.getSnapshot(), { completed: 1, total: 2 });
  assert.equal(controller.getActivityCompletion("first"), true);
  assert.equal(controller.getActivityCompletion("second"), false);
});


test("częściowy reset odczytuje tylko wskazane śledzone aktywności", async () => {
  const store = new ObservableMemoryStore({
    first: { status: "completed" },
    second: { status: "completed" },
    orphan: { status: "completed" },
  });
  const controller = createGlobalProgressController({
    manifest: manifest("first", "second"),
    store,
  });
  await controller.ready;
  store.getCalls.length = 0;

  store.reset(["first", "orphan", "first"]);
  await controller.whenIdle();

  assert.deepEqual(controller.getSnapshot(), { completed: 1, total: 2 });
  assert.deepEqual(store.getCalls, ["first"]);
});


test("reset single choice przez notifier aktualizuje centralny model", async () => {
  const document = createFakeDocument();
  const activity = {
    activity_id: "first",
    version: 1,
    label: "Pytanie",
    prompt: "Wybierz poprawną odpowiedź.",
    options: [
      { option_id: "a", label: "Pierwsza" },
      { option_id: "b", label: "Druga" },
    ],
    correct_option_id: "b",
    feedback: {
      correct: "To właściwa odpowiedź.",
      incorrect: "Sprawdź odpowiedzi ponownie.",
    },
    solution: {
      discussion: "Druga odpowiedź wynika z przebiegu pokazanego w materiale.",
    },
  };
  const delegate = new MemoryProgressStore({
    first: {
      status: "completed",
      score: 1,
      attempts: 2,
      payload: { selected_option_id: "b", last_result: "correct" },
    },
    second: { status: "completed", score: 1, attempts: 1 },
  });
  const store = new NotifyingProgressStore(delegate);
  const controller = createGlobalProgressController({
    manifest: manifest("first", "second"),
    store,
  });
  await controller.ready;
  const activityRoot = await renderSingleChoice({ activity, store, document });
  const restartButton = findElement(
    activityRoot,
    (element) => element.tagName === "button"
      && element.textContent === "Zacznij od nowa",
  );

  assert.deepEqual(controller.getSnapshot(), { completed: 2, total: 2 });
  await dispatch(restartButton, "click");
  await controller.whenIdle();

  assert.deepEqual(controller.getSnapshot(), { completed: 1, total: 2 });
  assert.equal(await delegate.get("first"), null);
  assert.equal((await delegate.get("second")).status, "completed");
});


test("Zacznij od nowa w code aktualizuje model i nie rusza innych aktywności", async () => {
  const document = createFakeDocument();
  const activity = {
    activity_id: "first",
    version: 1,
    label: "Ćwiczenie z kodem",
    prompt: "Wypisz tekst.",
    starter_code: "print('start')\n",
    checker: {
      type: "stdout_lines_exact",
      expected_lines: ["start"],
    },
    feedback: {
      correct: "Program wypisał oczekiwany tekst.",
      incorrect: "Sprawdź wypisywany tekst.",
    },
    solution: {
      code: "print('start')\n",
      discussion: "Wywołanie print wypisuje oczekiwany tekst.",
    },
  };
  const delegate = new MemoryProgressStore({
    first: {
      status: "completed",
      score: 1,
      attempts: 2,
      payload: { source_code: "print('ukończono')" },
    },
    second: { status: "completed", score: 1, attempts: 1 },
  });
  const store = new NotifyingProgressStore(delegate);
  const controller = createGlobalProgressController({
    manifest: manifest("first", "second"),
    store,
  });
  await controller.ready;
  const renderCode = createCodeRenderer({
    runtime: {
      async run() {
        return { stdout: "", stderr: "" };
      },
      stop() {},
      reset() {},
    },
  });
  const activityRoot = await renderCode({ activity, store, document });
  const editor = findElement(
    activityRoot,
    (element) => element.tagName === "textarea",
  );
  editor.focus = () => {};
  const restartButton = findElement(
    activityRoot,
    (element) => element.tagName === "button"
      && element.textContent === "Zacznij od nowa",
  );

  assert.deepEqual(controller.getSnapshot(), { completed: 2, total: 2 });
  await dispatch(restartButton, "click");
  await controller.whenIdle();

  assert.deepEqual(controller.getSnapshot(), { completed: 1, total: 2 });
  assert.equal(await delegate.get("first"), null);
  assert.equal((await delegate.get("second")).status, "completed");
});


test("pełny reset zeruje śledzony postęp bez dodatkowych odczytów", async () => {
  const store = new ObservableMemoryStore({
    first: { status: "completed" },
    second: { status: "completed" },
  });
  const controller = createGlobalProgressController({
    manifest: manifest("first", "second"),
    store,
  });
  await controller.ready;
  store.getCalls.length = 0;

  store.reset();
  await controller.whenIdle();

  assert.deepEqual(controller.getSnapshot(), { completed: 0, total: 2 });
  assert.deepEqual(store.getCalls, []);
});


test("po reloadzie model odtwarza istniejący postęp ze store", async () => {
  const store = new ObservableMemoryStore({
    first: { status: "completed" },
  });
  const firstController = createGlobalProgressController({
    manifest: manifest("first", "second"),
    store,
  });
  await firstController.ready;
  firstController.destroy();

  const reloadedController = createGlobalProgressController({
    manifest: manifest("first", "second"),
    store,
  });
  await reloadedController.ready;

  assert.deepEqual(reloadedController.getSnapshot(), {
    completed: 1,
    total: 2,
  });
});


test("późniejszy błędny wynik nie zmniejsza ukończenia", async () => {
  const store = new ObservableMemoryStore({
    first: { status: "completed", score: 1 },
  });
  const controller = createGlobalProgressController({
    manifest: manifest("first"),
    store,
  });
  await controller.ready;

  store.set("first", {
    status: "completed",
    score: 1,
    payload: { last_result: "incorrect" },
  });
  await controller.whenIdle();

  assert.deepEqual(controller.getSnapshot(), { completed: 1, total: 1 });
});


test("pusty manifest tworzy pusty model bez odczytów store", async () => {
  const store = new ObservableMemoryStore();
  const controller = createGlobalProgressController({
    manifest: manifest(),
    store,
  });
  await controller.ready;

  assert.deepEqual(controller.getSnapshot(), { completed: 0, total: 0 });
  assert.deepEqual(store.getCalls, []);
});


test("zdarzenie podczas wolnej hydracji jest zastosowane po jej wyniku", async () => {
  const store = new ObservableMemoryStore();
  const originalGet = store.get.bind(store);
  let releaseHydration;
  let firstGet = true;
  store.get = async (activityId) => {
    if (!firstGet) {
      return originalGet(activityId);
    }
    firstGet = false;
    const staleState = null;
    return new Promise((resolve) => {
      releaseHydration = () => resolve(staleState);
    });
  };

  const controller = createGlobalProgressController({
    manifest: manifest("first"),
    store,
  });
  await Promise.resolve();
  store.set("first", { status: "completed" });
  releaseHydration();

  await controller.ready;
  await controller.whenIdle();
  assert.deepEqual(controller.getSnapshot(), { completed: 1, total: 1 });
});


test("błąd początkowego odczytu pozostawia model niedostępny", async (t) => {
  const store = new ObservableMemoryStore();
  const readError = new Error("read failed");
  store.get = async () => {
    throw readError;
  };
  t.mock.method(console, "error", () => {});
  const controller = createGlobalProgressController({
    manifest: manifest("first"),
    store,
  });

  await assert.rejects(controller.ready, readError);

  assert.equal(controller.getActivityCompletion("first"), undefined);
});


test("udostępnia wyłącznie gotowy status pojedynczej śledzonej aktywności", async () => {
  const store = new ObservableMemoryStore({
    first: { status: "completed" },
    second: { status: "in_progress" },
  });
  const controller = createGlobalProgressController({
    manifest: manifest("first", "second"),
    store,
  });

  assert.equal(controller.getActivityCompletion("first"), undefined);
  await controller.ready;
  assert.equal(controller.getActivityCompletion("first"), true);
  assert.equal(controller.getActivityCompletion("second"), false);
  assert.equal(controller.getActivityCompletion("orphan"), undefined);

  controller.destroy();
  assert.equal(controller.getActivityCompletion("first"), undefined);
});


test("powiadamia unikalnymi ID dopiero po aktualizacji cache ukończeń", async () => {
  const store = new ObservableMemoryStore();
  const controller = createGlobalProgressController({
    manifest: manifest("first", "second"),
    store,
  });
  const events = [];
  const unsubscribe = controller.subscribeActivityCompletion((event) => {
    events.push({
      activityIds: [...event.activityIds],
      first: controller.getActivityCompletion("first"),
      frozenEvent: Object.isFrozen(event),
      frozenIds: Object.isFrozen(event.activityIds),
    });
  });

  await controller.ready;
  assert.deepEqual(events, []);

  store.set("first", { status: "completed" });
  await controller.whenIdle();
  assert.deepEqual(events, [{
    activityIds: ["first"],
    first: true,
    frozenEvent: true,
    frozenIds: true,
  }]);

  store.reset(["first", "orphan", "first"]);
  await controller.whenIdle();
  assert.deepEqual(events.at(-1).activityIds, ["first"]);
  assert.equal(events.at(-1).first, false);

  store.getCalls.length = 0;
  store.reset();
  await controller.whenIdle();
  assert.deepEqual(events.at(-1).activityIds, ["first", "second"]);
  assert.deepEqual(store.getCalls, []);

  unsubscribe();
  unsubscribe();
  store.set("first", { status: "completed" });
  await controller.whenIdle();
  assert.equal(events.length, 3);
});


test("błąd listenera nie blokuje pozostałych ani centralnego modelu", async (t) => {
  const store = new ObservableMemoryStore();
  const controller = createGlobalProgressController({
    manifest: manifest("first"),
    store,
  });
  await controller.ready;
  const errorLog = t.mock.method(console, "error", () => {});
  let successfulListenerCalls = 0;
  controller.subscribeActivityCompletion(() => {
    throw new Error("listener failed");
  });
  controller.subscribeActivityCompletion(() => {
    successfulListenerCalls += 1;
  });

  store.set("first", { status: "completed" });
  await controller.whenIdle();

  assert.equal(successfulListenerCalls, 1);
  assert.equal(errorLog.mock.callCount(), 1);
  assert.deepEqual(controller.getSnapshot(), { completed: 1, total: 1 });
});
