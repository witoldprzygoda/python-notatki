let pyodidePromise;
let configuredBaseUrl;
let currentExecution;

const OUTPUT_MESSAGE_CHUNK_SIZE = 1024;
const ERROR_MESSAGE_LIMIT = 8192;


function post(type, requestId, details = {}) {
  self.postMessage({
    type,
    request_id: requestId,
    ...details,
  });
}


async function getPyodide(baseUrl, requestId) {
  if (configuredBaseUrl && configuredBaseUrl !== baseUrl) {
    throw new Error("Nie można zmienić źródła Pyodide w aktywnym Workerze.");
  }

  if (!pyodidePromise) {
    configuredBaseUrl = baseUrl;
    post("state", requestId, { state: "loading" });
    const moduleUrl = new URL("pyodide.mjs", baseUrl);
    pyodidePromise = import(moduleUrl.href).then(
      ({ loadPyodide }) => loadPyodide({ indexURL: baseUrl }),
    );
  }

  try {
    return await pyodidePromise;
  } catch (error) {
    pyodidePromise = undefined;
    configuredBaseUrl = undefined;
    throw error;
  }
}


function destroyProxy(value) {
  if (value && typeof value.destroy === "function") {
    value.destroy();
  }
}


function errorDetails(error) {
  const rawMessage = error?.message || String(error);
  const message = rawMessage.length > ERROR_MESSAGE_LIMIT
    ? `${rawMessage.slice(0, ERROR_MESSAGE_LIMIT)}\n… komunikat błędu skrócono.`
    : rawMessage;
  return {
    name: error?.name || "Error",
    message,
  };
}


function flushPythonStreams(pyodide) {
  let flushResult;
  try {
    flushResult = pyodide.runPython(
      "import sys\nsys.stdout.flush()\nsys.stderr.flush()",
    );
  } finally {
    destroyProxy(flushResult);
  }
}


class OutputWriter {
  constructor(pyodide, stream, capacity) {
    this.pyodide = pyodide;
    this.stream = stream;
    this.bytes = new Uint8Array(capacity);
    this.length = 0;
    this.sentOffset = 0;
    this.decoder = new TextDecoder();
    this.isatty = false;
  }

  write(buffer) {
    const execution = currentExecution;
    if (!execution || execution.outputLimitExceeded) {
      return buffer.length;
    }

    const remaining = execution.outputLimit - execution.outputSize;
    const acceptedSize = Math.min(buffer.length, Math.max(remaining, 0));
    if (acceptedSize > 0) {
      const accepted = buffer.subarray(0, acceptedSize);
      this.bytes.set(accepted, this.length);
      this.length += accepted.length;
      execution.outputSize += accepted.length;
      this.#emitPending(false);
    }

    if (acceptedSize < buffer.length) {
      execution.outputLimitExceeded = true;
      execution.stdoutWriter.flush();
      execution.stderrWriter.flush();
      post("output_limit", execution.requestId, {
        limit: execution.outputLimit,
      });
      execution.interruptBuffer[0] = 2;
      this.pyodide.checkInterrupt();
      throw new Error("Przekroczono limit wyjścia.");
    }

    return buffer.length;
  }

  flush() {
    this.#emitPending(true);
  }

  #emitPending(final) {
    const pendingSize = this.length - this.sentOffset;
    if (!final && pendingSize < OUTPUT_MESSAGE_CHUNK_SIZE) {
      return;
    }

    const pending = this.bytes.subarray(this.sentOffset, this.length);
    this.sentOffset = this.length;
    const chunk = this.decoder.decode(pending, { stream: !final });
    if (chunk && currentExecution) {
      post("output", currentExecution.requestId, {
        stream: this.stream,
        chunk,
      });
    }
  }
}


self.addEventListener("message", async (event) => {
  const message = event.data;
  if (!message || message.type !== "run") {
    return;
  }

  const requestId = message.request_id;
  if (currentExecution) {
    post("runtime_error", requestId, {
      error: { message: "Inne wykonanie jest już aktywne." },
    });
    return;
  }

  currentExecution = {
    requestId,
    outputLimit: message.output_limit,
    outputSize: 0,
    outputLimitExceeded: false,
    interruptBuffer: new Uint8Array(1),
  };

  let phase = "load";
  let globals;
  let result;
  let stdoutWriter;
  let stderrWriter;
  try {
    const pyodide = await getPyodide(message.pyodide_base_url, requestId);
    phase = "execute";
    pyodide.setInterruptBuffer(currentExecution.interruptBuffer);
    stdoutWriter = new OutputWriter(
      pyodide,
      "stdout",
      currentExecution.outputLimit,
    );
    stderrWriter = new OutputWriter(
      pyodide,
      "stderr",
      currentExecution.outputLimit,
    );
    currentExecution.stdoutWriter = stdoutWriter;
    currentExecution.stderrWriter = stderrWriter;
    pyodide.setStdout(stdoutWriter);
    pyodide.setStderr(stderrWriter);
    globals = pyodide.toPy({ __name__: "__main__" });
    post("state", requestId, { state: "running" });
    result = pyodide.runPython(message.code, {
      globals,
      filename: "activity.py",
    });
    flushPythonStreams(pyodide);
    stdoutWriter.flush();
    stderrWriter.flush();
    if (!currentExecution.outputLimitExceeded) {
      post("finished", requestId);
    }
  } catch (error) {
    if (!currentExecution?.outputLimitExceeded) {
      if (phase === "execute") {
        try {
          const pyodide = await pyodidePromise;
          flushPythonStreams(pyodide);
        } catch (flushError) {
          void flushError;
        }
      }
      stdoutWriter?.flush();
      stderrWriter?.flush();
      if (!currentExecution?.outputLimitExceeded) {
        const type = phase === "load" ? "runtime_error" : "execution_error";
        post(type, requestId, {
          error: errorDetails(error),
        });
      }
    }
  } finally {
    destroyProxy(result);
    destroyProxy(globals);
    currentExecution = null;
  }
});
