function previousAttempts(state) {
  return Number.isInteger(state?.attempts) && state.attempts >= 0
    ? state.attempts
    : 0;
}


function wasCompleted(state) {
  return state?.status === "completed" || state?.score === 1;
}


export function deriveCodeControlState({
  preparing,
  running,
  checking,
  executionIsCurrent,
}) {
  const busy = preparing || running || checking;
  return {
    editorDisabled: busy,
    runDisabled: busy,
    stopDisabled: !running,
    resetDisabled: preparing || checking,
    checkDisabled: busy || !executionIsCurrent,
  };
}


function indentationWidth(line) {
  if (line.startsWith("\t")) {
    return 1;
  }
  const spaces = line.match(/^ {1,4}/);
  return spaces ? spaces[0].length : 0;
}


export function applyCodeIndentation(
  value,
  selectionStart,
  selectionEnd,
  outdent = false,
) {
  if (!outdent) {
    const indentation = "    ";
    const cursor = selectionStart + indentation.length;
    return {
      value:
        value.slice(0, selectionStart)
        + indentation
        + value.slice(selectionEnd),
      selectionStart: cursor,
      selectionEnd: cursor,
    };
  }

  const blockStart = value.lastIndexOf("\n", selectionStart - 1) + 1;
  let blockEnd;
  if (selectionEnd > selectionStart && value[selectionEnd - 1] === "\n") {
    blockEnd = selectionEnd - 1;
  } else {
    const nextLineBreak = value.indexOf("\n", selectionEnd);
    blockEnd = nextLineBreak === -1 ? value.length : nextLineBreak;
  }

  const block = value.slice(blockStart, blockEnd);
  const removals = [];
  let lineStart = blockStart;
  const transformedBlock = block
    .split("\n")
    .map((line) => {
      const width = indentationWidth(line);
      if (width > 0) {
        removals.push({ start: lineStart, width });
      }
      lineStart += line.length + 1;
      return line.slice(width);
    })
    .join("\n");

  function adjustedPosition(position) {
    let removed = 0;
    for (const removal of removals) {
      if (position <= removal.start) {
        break;
      }
      removed += Math.min(removal.width, position - removal.start);
    }
    return position - removed;
  }

  return {
    value:
      value.slice(0, blockStart)
      + transformedBlock
      + value.slice(blockEnd),
    selectionStart: adjustedPosition(selectionStart),
    selectionEnd: adjustedPosition(selectionEnd),
  };
}


export function createCodeRunProgressState(
  activity,
  previousState,
  sourceCode,
) {
  const completed = wasCompleted(previousState);
  return {
    version: activity.version,
    status: completed ? "completed" : "in_progress",
    score: completed ? 1 : 0,
    attempts: previousAttempts(previousState),
    payload: {
      source_code: sourceCode,
    },
  };
}


export function createCodeCheckProgressState(
  activity,
  previousState,
  sourceCode,
  isCorrect,
) {
  const completed = wasCompleted(previousState) || isCorrect;
  return {
    version: activity.version,
    status: completed ? "completed" : "in_progress",
    score: completed ? 1 : 0,
    attempts: previousAttempts(previousState) + 1,
    payload: {
      source_code: sourceCode,
      last_result: isCorrect ? "correct" : "incorrect",
    },
  };
}


function outputLines(output) {
  let normalized = output.replace(/\r\n?/g, "\n");
  if (normalized === "") {
    return [];
  }
  if (normalized.endsWith("\n")) {
    normalized = normalized.slice(0, -1);
  }
  return normalized.split("\n");
}


export function checkCodeResult(activity, execution) {
  if (activity.checker?.type !== "stdout_lines_exact") {
    throw new Error(`Nieobsługiwany checker ${activity.checker?.type}.`);
  }
  if (
    !execution
    || execution.error
    || typeof execution.stdout !== "string"
    || typeof execution.stderr !== "string"
    || execution.stderr !== ""
  ) {
    return false;
  }

  const actualLines = outputLines(execution.stdout);
  const expectedLines = activity.checker.expected_lines;
  return (
    actualLines.length === expectedLines.length
    && actualLines.every((line, index) => line === expectedLines[index])
  );
}


function setProgressSummary(element, state) {
  const completion = wasCompleted(state) ? " Aktywność ukończona." : "";
  element.textContent =
    `Liczba prób sprawdzenia: ${previousAttempts(state)}.${completion}`;
}


function appendError(stderrElement, message) {
  const separator = stderrElement.textContent
    && !stderrElement.textContent.endsWith("\n")
    ? "\n"
    : "";
  stderrElement.textContent += `${separator}${message}\n`;
}


function restoreFeedback(activity, state, feedback) {
  const lastResult = state?.payload?.last_result;
  if (lastResult === "correct" || lastResult === "incorrect") {
    feedback.textContent = activity.feedback[lastResult];
    feedback.hidden = false;
  }
}


function requireRuntime(runtime) {
  if (
    !runtime
    || typeof runtime.run !== "function"
    || typeof runtime.stop !== "function"
    || typeof runtime.reset !== "function"
  ) {
    throw new TypeError("Renderer code wymaga poprawnego PyodideRuntime.");
  }
}


export function createCodeRenderer({ runtime }) {
  requireRuntime(runtime);

  return async function renderCode({ activity, store, document }) {
    const section = document.createElement("section");
    section.className = "interactive-activity interactive-activity--code";
    section.dataset.activityId = activity.activity_id;

    const heading = document.createElement("h3");
    heading.textContent = activity.label;

    const prompt = document.createElement("p");
    prompt.className = "interactive-activity__prompt";
    const promptLabel = document.createElement("strong");
    promptLabel.textContent = "Polecenie:";
    prompt.append(promptLabel, ` ${activity.prompt}`);

    const editorLabel = document.createElement("label");
    const editorId = `code-editor-${activity.activity_id}`;
    editorLabel.htmlFor = editorId;
    editorLabel.textContent = "Kod Python";

    const editor = document.createElement("textarea");
    editor.id = editorId;
    editor.rows = 8;
    editor.spellcheck = false;
    editor.setAttribute("autocapitalize", "off");
    editor.setAttribute("autocomplete", "off");
    editor.value = activity.starter_code;

    const controls = document.createElement("div");
    controls.className = "interactive-activity__controls";

    const runButton = document.createElement("button");
    runButton.type = "button";
    runButton.textContent = "Uruchom";

    const stopButton = document.createElement("button");
    stopButton.type = "button";
    stopButton.textContent = "Zatrzymaj";
    stopButton.disabled = true;

    const resetButton = document.createElement("button");
    resetButton.type = "button";
    resetButton.textContent = "Resetuj interpreter";

    const checkButton = document.createElement("button");
    checkButton.type = "button";
    checkButton.textContent = "Sprawdź";
    checkButton.disabled = true;

    controls.append(runButton, stopButton, resetButton, checkButton);

    const status = document.createElement("p");
    status.setAttribute("aria-live", "polite");
    status.textContent = "Interpreter nie został jeszcze uruchomiony.";

    const stdoutLabel = document.createElement("p");
    stdoutLabel.textContent = "Standardowe wyjście (stdout)";
    const stdout = document.createElement("pre");
    stdout.className = "interactive-activity__output";

    const stderrLabel = document.createElement("p");
    stderrLabel.textContent = "Błędy i komunikaty diagnostyczne (stderr)";
    const stderr = document.createElement("pre");
    stderr.className = "interactive-activity__output";

    const feedback = document.createElement("p");
    feedback.setAttribute("aria-live", "polite");
    feedback.hidden = true;

    const summary = document.createElement("p");
    let savedState = null;
    try {
      savedState = await store.get(activity.activity_id);
      const sourceCode = savedState?.payload?.source_code;
      if (typeof sourceCode === "string") {
        editor.value = sourceCode;
      }
      restoreFeedback(activity, savedState, feedback);
      setProgressSummary(summary, savedState);
    } catch (error) {
      summary.textContent = "Nie można odczytać lokalnego stanu aktywności.";
      console.warn("Nie udało się odczytać postępu aktywności code.", error);
    }

    let preparing = false;
    let running = false;
    let checking = false;
    let lastExecution = null;

    function updateControls() {
      const controlState = deriveCodeControlState({
        preparing,
        running,
        checking,
        executionIsCurrent:
          Boolean(lastExecution)
          && lastExecution.sourceCode === editor.value,
      });
      editor.disabled = controlState.editorDisabled;
      runButton.disabled = controlState.runDisabled;
      stopButton.disabled = controlState.stopDisabled;
      resetButton.disabled = controlState.resetDisabled;
      checkButton.disabled = controlState.checkDisabled;
    }

    function invalidateExecution() {
      lastExecution = null;
      feedback.textContent = "";
      feedback.hidden = true;
      updateControls();
    }

    function handleEditorChange() {
      if (lastExecution?.sourceCode !== editor.value) {
        invalidateExecution();
        status.textContent = "Kod zmieniono. Uruchom go ponownie przed sprawdzeniem.";
      }
    }

    editor.addEventListener("input", handleEditorChange);

    editor.addEventListener("keydown", (event) => {
      if (event.key !== "Tab") {
        return;
      }

      const previousValue = editor.value;
      const indentation = applyCodeIndentation(
        previousValue,
        editor.selectionStart,
        editor.selectionEnd,
        event.shiftKey,
      );
      if (event.shiftKey && indentation.value === previousValue) {
        return;
      }

      event.preventDefault();
      editor.value = indentation.value;
      editor.setSelectionRange(
        indentation.selectionStart,
        indentation.selectionEnd,
      );
      if (editor.value !== previousValue) {
        handleEditorChange();
      }
    });

    runButton.addEventListener("click", async () => {
      const sourceCode = editor.value;
      invalidateExecution();
      stdout.textContent = "";
      stderr.textContent = "";
      preparing = true;
      status.textContent = "Zapisywanie kodu przed uruchomieniem…";
      updateControls();

      let progressSaved = true;
      try {
        const currentState = await store.get(activity.activity_id);
        savedState = await store.save(
          activity.activity_id,
          createCodeRunProgressState(activity, currentState, sourceCode),
        );
        setProgressSummary(summary, savedState);
      } catch (error) {
        progressSaved = false;
        summary.textContent = "Nie udało się zapisać kodu i postępu aktywności.";
        console.warn("Nie udało się zapisać postępu aktywności code.", error);
      }

      preparing = false;
      running = true;
      updateControls();
      try {
        const result = await runtime.run(sourceCode, {
          onState: (runtimeState) => {
            status.textContent = runtimeState === "loading"
              ? "Ładowanie interpretera Python…"
              : "Wykonywanie kodu…";
          },
          onOutput: ({ stream, chunk }) => {
            const output = stream === "stdout" ? stdout : stderr;
            output.textContent += chunk;
          },
        });
        stdout.textContent = result.stdout;
        stderr.textContent = result.stderr;
        lastExecution = {
          sourceCode,
          stdout: result.stdout,
          stderr: result.stderr,
        };
        status.textContent = progressSaved
          ? "Wykonanie zakończone. Można sprawdzić wynik."
          : "Wykonanie zakończone, ale nie zapisano lokalnego postępu.";
      } catch (error) {
        lastExecution = null;
        if (error?.code === "reset") {
          stdout.textContent = "";
          stderr.textContent = "";
        } else {
          if (typeof error?.stdout === "string") {
            stdout.textContent = error.stdout;
          }
          if (typeof error?.stderr === "string") {
            stderr.textContent = error.stderr;
          }
        }

        if (error?.code === "stopped") {
          status.textContent = "Wykonanie zatrzymano. Kolejny Run utworzy nowy interpreter.";
        } else if (error?.code === "reset") {
          status.textContent = "Interpreter zresetowano.";
        } else {
          appendError(stderr, error?.message || "Nie udało się wykonać kodu.");
          status.textContent = "Wykonanie zakończyło się błędem.";
        }
      } finally {
        preparing = false;
        running = false;
        updateControls();
      }
    });

    stopButton.addEventListener("click", () => {
      runtime.stop();
      invalidateExecution();
      status.textContent = "Zatrzymywanie wykonania…";
    });

    resetButton.addEventListener("click", () => {
      runtime.reset();
      invalidateExecution();
      stdout.textContent = "";
      stderr.textContent = "";
      status.textContent = "Interpreter zresetowano. Następny Run załaduje go ponownie.";
    });

    checkButton.addEventListener("click", async () => {
      if (!lastExecution || lastExecution.sourceCode !== editor.value) {
        return;
      }

      checking = true;
      try {
        updateControls();

        let isCorrect;
        try {
          isCorrect = checkCodeResult(activity, lastExecution);
        } catch (error) {
          feedback.textContent =
            "Nie można sprawdzić rozwiązania z powodu błędu konfiguracji aktywności.";
          feedback.hidden = false;
          console.error("Błąd konfiguracji checkera aktywności code.", error);
          return;
        }

        try {
          const currentState = await store.get(activity.activity_id);
          const nextState = createCodeCheckProgressState(
            activity,
            currentState,
            editor.value,
            isCorrect,
          );
          savedState = await store.save(activity.activity_id, nextState);
          feedback.textContent = activity.feedback[nextState.payload.last_result];
          feedback.hidden = false;
          setProgressSummary(summary, savedState);
        } catch (error) {
          feedback.textContent = "Nie udało się zapisać wyniku sprawdzenia.";
          feedback.hidden = false;
          console.warn("Nie udało się zapisać postępu aktywności code.", error);
        }
      } finally {
        checking = false;
        updateControls();
      }
    });

    section.append(
      heading,
      prompt,
      editorLabel,
      editor,
      controls,
      status,
      stdoutLabel,
      stdout,
      stderrLabel,
      stderr,
      feedback,
      summary,
    );
    return section;
  };
}
