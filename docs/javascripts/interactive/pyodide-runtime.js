export const DEFAULT_PYODIDE_BASE_URL =
  "https://cdn.jsdelivr.net/pyodide/v314.0.4/full/";

export const DEFAULT_OUTPUT_LIMIT = 64 * 1024;


function defaultWorkerFactory(url, options) {
  return new Worker(url, options);
}


function requireFunction(value, name) {
  if (typeof value !== "function") {
    throw new TypeError(`${name} musi być funkcją.`);
  }
}


export class PyodideRuntimeError extends Error {
  constructor(message, { code, stdout = "", stderr = "" }) {
    super(message);
    this.name = "PyodideRuntimeError";
    this.code = code;
    this.stdout = stdout;
    this.stderr = stderr;
  }
}


export class PyodideRuntime {
  constructor({
    workerUrl = new URL("./pyodide-worker.js", import.meta.url),
    pyodideBaseUrl = DEFAULT_PYODIDE_BASE_URL,
    outputLimit = DEFAULT_OUTPUT_LIMIT,
    workerFactory = defaultWorkerFactory,
  } = {}) {
    if (!(workerUrl instanceof URL) && typeof workerUrl !== "string") {
      throw new TypeError("workerUrl musi być adresem URL lub tekstem.");
    }
    if (typeof pyodideBaseUrl !== "string" || !pyodideBaseUrl.endsWith("/")) {
      throw new TypeError("pyodideBaseUrl musi być tekstem zakończonym znakiem '/'.");
    }
    if (!Number.isInteger(outputLimit) || outputLimit < 1) {
      throw new TypeError("outputLimit musi być dodatnią liczbą całkowitą.");
    }
    requireFunction(workerFactory, "workerFactory");

    this.workerUrl = workerUrl;
    this.pyodideBaseUrl = pyodideBaseUrl;
    this.outputLimit = outputLimit;
    this.workerFactory = workerFactory;
    this.worker = null;
    this.workerListeners = null;
    this.currentRun = null;
    this.nextRequestId = 1;
  }

  run(code, { onState = () => {}, onOutput = () => {} } = {}) {
    if (typeof code !== "string") {
      return Promise.reject(new TypeError("Kod Pythona musi być tekstem."));
    }
    try {
      requireFunction(onState, "onState");
      requireFunction(onOutput, "onOutput");
    } catch (error) {
      return Promise.reject(error);
    }
    if (this.currentRun) {
      return Promise.reject(
        new PyodideRuntimeError("Inne wykonanie jest już aktywne.", {
          code: "busy",
        }),
      );
    }

    let worker;
    try {
      worker = this.#ensureWorker();
    } catch (error) {
      return Promise.reject(
        new PyodideRuntimeError(
          error instanceof Error ? error.message : "Nie można utworzyć Workera.",
          { code: "worker_error" },
        ),
      );
    }

    const requestId = this.nextRequestId;
    this.nextRequestId += 1;

    return new Promise((resolve, reject) => {
      this.currentRun = {
        requestId,
        stdout: "",
        stderr: "",
        onState,
        onOutput,
        resolve,
        reject,
      };

      try {
        worker.postMessage({
          type: "run",
          request_id: requestId,
          code,
          pyodide_base_url: this.pyodideBaseUrl,
          output_limit: this.outputLimit,
        });
      } catch (error) {
        const currentRun = this.currentRun;
        this.currentRun = null;
        this.#terminateWorker();
        currentRun.reject(
          new PyodideRuntimeError(
            error instanceof Error
              ? error.message
              : "Nie można wysłać kodu do Workera.",
            { code: "worker_error" },
          ),
        );
      }
    });
  }

  stop() {
    return this.#abort("stopped", "Wykonanie zostało zatrzymane.");
  }

  reset() {
    return this.#abort("reset", "Interpreter został zresetowany.");
  }

  #ensureWorker() {
    if (this.worker) {
      return this.worker;
    }

    const worker = this.workerFactory(this.workerUrl, { type: "module" });
    if (
      !worker
      || typeof worker.postMessage !== "function"
      || typeof worker.terminate !== "function"
      || typeof worker.addEventListener !== "function"
    ) {
      throw new TypeError("workerFactory musi zwracać obiekt zgodny z Worker.");
    }

    const messageListener = (event) => {
      this.#handleMessage(worker, event.data);
    };
    const errorListener = (event) => {
      this.#handleWorkerFailure(
        worker,
        event?.message || "Worker Pyodide zakończył się błędem.",
      );
    };
    const messageErrorListener = () => {
      this.#handleWorkerFailure(
        worker,
        "Worker Pyodide przesłał niepoprawną wiadomość.",
      );
    };

    worker.addEventListener("message", messageListener);
    worker.addEventListener("error", errorListener);
    worker.addEventListener("messageerror", messageErrorListener);
    this.worker = worker;
    this.workerListeners = {
      messageListener,
      errorListener,
      messageErrorListener,
    };
    return worker;
  }

  #handleMessage(worker, message) {
    if (worker !== this.worker || !message || typeof message !== "object") {
      return;
    }

    const currentRun = this.currentRun;
    if (!currentRun || message.request_id !== currentRun.requestId) {
      return;
    }

    if (message.type === "state") {
      currentRun.onState(message.state);
      return;
    }

    if (message.type === "output") {
      if (
        (message.stream !== "stdout" && message.stream !== "stderr")
        || typeof message.chunk !== "string"
      ) {
        return;
      }
      currentRun[message.stream] += message.chunk;
      currentRun.onOutput({
        stream: message.stream,
        chunk: message.chunk,
      });
      return;
    }

    if (message.type === "finished") {
      this.currentRun = null;
      currentRun.resolve({
        stdout: currentRun.stdout,
        stderr: currentRun.stderr,
      });
      return;
    }

    if (message.type === "execution_error") {
      this.currentRun = null;
      currentRun.reject(
        new PyodideRuntimeError(
          message.error?.message || "Wykonanie kodu Python zakończyło się błędem.",
          {
            code: "execution_error",
            stdout: currentRun.stdout,
            stderr: currentRun.stderr,
          },
        ),
      );
      return;
    }

    if (message.type === "output_limit") {
      this.currentRun = null;
      this.#terminateWorker();
      currentRun.reject(
        new PyodideRuntimeError(
          `Przekroczono limit ${message.limit} bajtów wyjścia. Wykonanie przerwano.`,
          {
            code: "output_limit",
            stdout: currentRun.stdout,
            stderr: currentRun.stderr,
          },
        ),
      );
      return;
    }

    if (message.type === "runtime_error") {
      this.currentRun = null;
      this.#terminateWorker();
      currentRun.reject(
        new PyodideRuntimeError(
          message.error?.message || "Nie udało się uruchomić Pyodide.",
          {
            code: "runtime_error",
            stdout: currentRun.stdout,
            stderr: currentRun.stderr,
          },
        ),
      );
    }
  }

  #handleWorkerFailure(worker, message) {
    if (worker !== this.worker) {
      return;
    }
    const currentRun = this.currentRun;
    this.currentRun = null;
    this.#terminateWorker();
    if (currentRun) {
      currentRun.reject(
        new PyodideRuntimeError(message, {
          code: "worker_error",
          stdout: currentRun.stdout,
          stderr: currentRun.stderr,
        }),
      );
    }
  }

  #abort(code, message) {
    const hadWorker = this.worker !== null;
    const currentRun = this.currentRun;
    this.currentRun = null;
    this.#terminateWorker();
    if (currentRun) {
      currentRun.reject(
        new PyodideRuntimeError(message, {
          code,
          stdout: currentRun.stdout,
          stderr: currentRun.stderr,
        }),
      );
    }
    return hadWorker;
  }

  #terminateWorker() {
    if (!this.worker) {
      return;
    }

    const worker = this.worker;
    const listeners = this.workerListeners;
    this.worker = null;
    this.workerListeners = null;

    if (listeners && typeof worker.removeEventListener === "function") {
      worker.removeEventListener("message", listeners.messageListener);
      worker.removeEventListener("error", listeners.errorListener);
      worker.removeEventListener(
        "messageerror",
        listeners.messageErrorListener,
      );
    }
    worker.terminate();
  }
}
