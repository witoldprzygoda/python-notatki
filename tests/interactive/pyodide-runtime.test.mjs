import assert from "node:assert/strict";
import test from "node:test";

import {
  DEFAULT_PYODIDE_BASE_URL,
  PyodideRuntime,
} from "../../docs/javascripts/interactive/pyodide-runtime.js";


class FakeWorker {
  constructor(url, options) {
    this.url = url;
    this.options = options;
    this.listeners = new Map();
    this.messages = [];
    this.terminated = false;
  }

  addEventListener(type, listener) {
    const listeners = this.listeners.get(type) ?? new Set();
    listeners.add(listener);
    this.listeners.set(type, listeners);
  }

  removeEventListener(type, listener) {
    this.listeners.get(type)?.delete(listener);
  }

  postMessage(message) {
    this.messages.push(message);
  }

  terminate() {
    this.terminated = true;
  }

  emit(type, data) {
    for (const listener of this.listeners.get(type) ?? []) {
      listener(type === "message" ? { data } : data);
    }
  }
}


function createRuntime() {
  const workers = [];
  const runtime = new PyodideRuntime({
    workerUrl: "worker.js",
    workerFactory: (url, options) => {
      const worker = new FakeWorker(url, options);
      workers.push(worker);
      return worker;
    },
  });
  return { runtime, workers };
}


test("używa przypiętego Pyodide 314.0.4", () => {
  assert.equal(
    DEFAULT_PYODIDE_BASE_URL,
    "https://cdn.jsdelivr.net/pyodide/v314.0.4/full/",
  );
});


test("tworzy modułowego Workera dopiero przy pierwszym Run", async () => {
  const { runtime, workers } = createRuntime();
  assert.equal(workers.length, 0);

  const states = [];
  const chunks = [];
  const resultPromise = runtime.run("print('abc')", {
    onState: (state) => states.push(state),
    onOutput: (output) => chunks.push(output),
  });

  assert.equal(workers.length, 1);
  const worker = workers[0];
  assert.deepEqual(worker.options, { type: "module" });
  assert.equal(worker.messages[0].pyodide_base_url, DEFAULT_PYODIDE_BASE_URL);
  assert.equal(worker.messages[0].code, "print('abc')");

  const requestId = worker.messages[0].request_id;
  worker.emit("message", {
    type: "state",
    request_id: requestId,
    state: "loading",
  });
  worker.emit("message", {
    type: "state",
    request_id: requestId,
    state: "running",
  });
  worker.emit("message", {
    type: "output",
    request_id: requestId,
    stream: "stdout",
    chunk: "abc\n",
  });
  worker.emit("message", { type: "finished", request_id: requestId });

  assert.deepEqual(await resultPromise, {
    stdout: "abc\n",
    stderr: "",
  });
  assert.deepEqual(states, ["loading", "running"]);
  assert.deepEqual(chunks, [{ stream: "stdout", chunk: "abc\n" }]);
});


test("współdzieli Workera między zakończonymi uruchomieniami", async () => {
  const { runtime, workers } = createRuntime();
  const firstPromise = runtime.run("pierwszy = 1");
  const worker = workers[0];
  const firstRequestId = worker.messages[0].request_id;
  worker.emit("message", {
    type: "finished",
    request_id: firstRequestId,
  });
  await firstPromise;

  const secondPromise = runtime.run("print('drugi')");
  assert.equal(workers.length, 1);
  const secondRequestId = worker.messages[1].request_id;
  assert.notEqual(secondRequestId, firstRequestId);
  worker.emit("message", {
    type: "finished",
    request_id: secondRequestId,
  });
  await secondPromise;
});


test("Stop kończy Workera, a następny Run tworzy nowego", async () => {
  const { runtime, workers } = createRuntime();
  const firstPromise = runtime.run("while True: pass");
  assert.equal(runtime.stop(), true);
  assert.equal(workers[0].terminated, true);
  await assert.rejects(firstPromise, (error) => error.code === "stopped");

  const secondPromise = runtime.run("print('po stop')");
  assert.equal(workers.length, 2);
  const requestId = workers[1].messages[0].request_id;
  workers[1].emit("message", { type: "finished", request_id: requestId });
  await secondPromise;
});


test("Reset kończy także bezczynnego Workera", async () => {
  const { runtime, workers } = createRuntime();
  const resultPromise = runtime.run("pass");
  const requestId = workers[0].messages[0].request_id;
  workers[0].emit("message", { type: "finished", request_id: requestId });
  await resultPromise;

  assert.equal(runtime.reset(), true);
  assert.equal(workers[0].terminated, true);
});


test("przekroczenie limitu kończy Workera i zachowuje ograniczone wyjście", async () => {
  const { runtime, workers } = createRuntime();
  const resultPromise = runtime.run("print('dużo')");
  const worker = workers[0];
  const requestId = worker.messages[0].request_id;
  worker.emit("message", {
    type: "output",
    request_id: requestId,
    stream: "stdout",
    chunk: "częściowy wynik",
  });
  worker.emit("message", {
    type: "output_limit",
    request_id: requestId,
    limit: 65536,
  });

  await assert.rejects(
    resultPromise,
    (error) => (
      error.code === "output_limit"
      && error.stdout === "częściowy wynik"
    ),
  );
  assert.equal(worker.terminated, true);
});


test("odrzuca równoległy Run", async () => {
  const { runtime, workers } = createRuntime();
  const firstPromise = runtime.run("while True: pass");
  await assert.rejects(
    runtime.run("print('drugi')"),
    (error) => error.code === "busy",
  );
  runtime.stop();
  await assert.rejects(firstPromise, (error) => error.code === "stopped");
  assert.equal(workers.length, 1);
});
