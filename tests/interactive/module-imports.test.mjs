import assert from "node:assert/strict";
import test from "node:test";


class MemoryStorage {
  constructor() {
    this.items = new Map();
  }

  getItem(key) {
    return this.items.has(String(key)) ? this.items.get(String(key)) : null;
  }

  removeItem(key) {
    this.items.delete(String(key));
  }

  setItem(key, value) {
    this.items.set(String(key), String(value));
  }
}


test("bootstrap importuje wszystkie moduły bez tworzenia Workera", async () => {
  let subscribedCallback;
  let workerCreated = false;
  globalThis.window = { localStorage: new MemoryStorage() };
  globalThis.document$ = {
    subscribe(callback) {
      subscribedCallback = callback;
    },
  };
  globalThis.Worker = class {
    constructor() {
      workerCreated = true;
      throw new Error("Worker nie powinien powstać podczas importu.");
    }
  };

  try {
    await import("../../docs/javascripts/interactive/bootstrap.js?import-test");
    assert.equal(typeof subscribedCallback, "function");
    assert.equal(workerCreated, false);
  } finally {
    delete globalThis.Worker;
    delete globalThis.document$;
    delete globalThis.window;
  }
});
