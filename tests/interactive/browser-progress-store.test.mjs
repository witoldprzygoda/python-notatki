import assert from "node:assert/strict";
import test from "node:test";

import {
  BrowserProgressStore,
  DEFAULT_PROGRESS_STORAGE_KEY,
} from "../../docs/javascripts/interactive/browser-progress-store.js";


class MemoryStorage {
  constructor() {
    this.items = new Map();
  }

  get length() {
    return this.items.size;
  }

  clear() {
    this.items.clear();
  }

  getItem(key) {
    return this.items.has(String(key)) ? this.items.get(String(key)) : null;
  }

  key(index) {
    return Array.from(this.items.keys())[index] ?? null;
  }

  removeItem(key) {
    this.items.delete(String(key));
  }

  setItem(key, value) {
    this.items.set(String(key), String(value));
  }
}


test("zapisuje i odtwarza ukończenie według activity_id", async () => {
  const storage = new MemoryStorage();
  const store = new BrowserProgressStore(storage);

  const savedState = await store.save("flow-for-read-001", {
    version: 1,
    status: "completed",
  });

  assert.equal(savedState.activity_id, "flow-for-read-001");
  assert.equal(savedState.version, 1);
  assert.equal(savedState.status, "completed");
  assert.equal(Number.isNaN(Date.parse(savedState.updated_at)), false);

  const reloadedStore = new BrowserProgressStore(storage);
  assert.deepEqual(
    await reloadedStore.get("flow-for-read-001"),
    savedState,
  );
  assert.deepEqual(await reloadedStore.getSummary(), {
    total: 1,
    completed: 1,
  });
});


test("zapisuje wycofanie zaznaczenia bez osobnego resetu", async () => {
  const storage = new MemoryStorage();
  const store = new BrowserProgressStore(storage);

  await store.save("flow-for-read-001", {
    version: 1,
    status: "completed",
  });
  await store.save("flow-for-read-001", {
    version: 1,
    status: "not_started",
  });

  const reloadedStore = new BrowserProgressStore(storage);
  const state = await reloadedStore.get("flow-for-read-001");
  assert.equal(state.status, "not_started");
  assert.deepEqual(await reloadedStore.getSummary(), {
    total: 1,
    completed: 0,
  });
});


test("traktuje uszkodzony JSON jak pusty magazyn", async () => {
  const storage = new MemoryStorage();
  storage.setItem(DEFAULT_PROGRESS_STORAGE_KEY, "{niepoprawny-json");
  const store = new BrowserProgressStore(storage);

  assert.equal(await store.get("flow-for-read-001"), null);
  assert.deepEqual(await store.getSummary(), {
    total: 0,
    completed: 0,
  });

  await store.save("flow-for-read-001", {
    version: 1,
    status: "completed",
  });
  assert.doesNotThrow(() => {
    JSON.parse(storage.getItem(DEFAULT_PROGRESS_STORAGE_KEY));
  });
});


test("reset usuwa wyłącznie dokument postępu aplikacji", async () => {
  const storage = new MemoryStorage();
  storage.setItem("inny-klucz", "pozostaje");
  const store = new BrowserProgressStore(storage);
  await store.save("flow-for-read-001", {
    version: 1,
    status: "completed",
  });

  await store.reset();

  assert.equal(storage.getItem(DEFAULT_PROGRESS_STORAGE_KEY), null);
  assert.equal(storage.getItem("inny-klucz"), "pozostaje");
});


test("zachowuje pola postępu specyficzne dla aktywności", async () => {
  const storage = new MemoryStorage();
  const store = new BrowserProgressStore(storage);

  const savedState = await store.save("flow-for-quiz-001", {
    version: 1,
    status: "completed",
    score: 1,
    attempts: 2,
    payload: {
      selected_option_id: "b",
      last_result: "correct",
    },
  });

  assert.equal(savedState.score, 1);
  assert.equal(savedState.attempts, 2);
  assert.deepEqual(savedState.payload, {
    selected_option_id: "b",
    last_result: "correct",
  });
  assert.deepEqual(
    await new BrowserProgressStore(storage).get("flow-for-quiz-001"),
    savedState,
  );
});
