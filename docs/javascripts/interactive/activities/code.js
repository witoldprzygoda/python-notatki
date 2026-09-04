import { createActivityShell } from "../activity-dom.js";
import { createActivityHelp } from "../activity-help.js";
import {
  createCheckedProgressState,
  createCodeRunProgressState as createSharedCodeRunProgressState,
  createManualCompletionProgressState,
  isCompleted,
} from "../activity-progress-state.js";


function previousAttempts(state) {
  return Number.isInteger(state?.attempts) && state.attempts >= 0
    ? state.attempts
    : 0;
}


export function deriveCodeControlState({
  preparing,
  running,
  checking,
  restarting = false,
  savingCompletion = false,
  executionIsCurrent,
  workerAvailable = false,
  activityCanRestart = false,
}) {
  const busy =
    preparing || running || checking || restarting || savingCompletion;
  return {
    editorDisabled: busy,
    runDisabled: busy,
    stopDisabled: restarting || !running,
    resetDisabled:
      preparing
      || checking
      || restarting
      || savingCompletion
      || !workerAvailable,
    checkDisabled: busy || !executionIsCurrent,
    restartActivityDisabled:
      preparing
      || checking
      || restarting
      || savingCompletion
      || (!running && !activityCanRestart),
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
  return createSharedCodeRunProgressState(
    activity,
    previousState,
    sourceCode,
  );
}


export function createCodeCheckProgressState(
  activity,
  previousState,
  sourceCode,
  isCorrect,
  payloadPatch = {},
) {
  return createCheckedProgressState(activity, previousState, {
    isCorrect,
    payloadPatch: {
      ...payloadPatch,
      source_code: sourceCode,
      last_result: isCorrect ? "correct" : "incorrect",
    },
  });
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
  element.textContent = `Próby: ${previousAttempts(state)}`;
}


function appendError(stderrElement, message) {
  const separator = stderrElement.textContent
    && !stderrElement.textContent.endsWith("\n")
    ? "\n"
    : "";
  stderrElement.textContent += `${separator}${message}\n`;
}


function clearFeedback(feedback) {
  feedback.className = "interactive-activity__message";
  feedback.textContent = "";
  feedback.hidden = true;
}


function showFeedback(activity, result, feedback) {
  const correct = result === "correct";
  feedback.className =
    `interactive-activity__message interactive-activity__message--${result}`;

  const resultLabel = feedback.ownerDocument.createElement("strong");
  resultLabel.className = "interactive-activity__message-result";
  resultLabel.textContent = correct ? "✓ Poprawnie" : "! Niepoprawnie";

  const explanation = feedback.ownerDocument.createElement("span");
  explanation.className = "interactive-activity__message-explanation";
  explanation.textContent = correct
    ? activity.feedback.correct
    : activity.feedback.incorrect;

  feedback.replaceChildren(resultLabel, explanation);
  feedback.hidden = false;
}


function showTechnicalError(feedback, text) {
  feedback.className =
    "interactive-activity__message interactive-activity__message--error";
  feedback.textContent = `Błąd techniczny: ${text}`;
  feedback.hidden = false;
}


function restoreFeedback(activity, state, feedback) {
  const lastResult = state?.payload?.last_result;
  if (lastResult === "correct" || lastResult === "incorrect") {
    showFeedback(activity, lastResult, feedback);
  }
}


function createReadonlyCodeBlock(document, sourceCode) {
  const pre = document.createElement("pre");
  pre.className = "interactive-activity__solution-code";
  const code = document.createElement("code");
  code.textContent = sourceCode;
  pre.append(code);
  return pre;
}


function createCodeSolutionContent(document, activity) {
  const content = document.createElement("div");
  content.className = "interactive-activity__solution";

  const label = document.createElement("strong");
  label.className = "interactive-activity__solution-heading";
  label.textContent = "Przykładowe rozwiązanie";

  content.append(
    label,
    createReadonlyCodeBlock(document, activity.solution.code),
  );
  return content;
}


function createCodeDiscussionContent(document, activity) {
  const content = document.createElement("div");
  content.className = "interactive-activity__discussion";

  const explanationLabel = document.createElement("strong");
  explanationLabel.className = "interactive-activity__solution-heading";
  explanationLabel.textContent = "Dlaczego działa";

  const explanation = document.createElement("p");
  explanation.className = "interactive-activity__discussion-text";
  explanation.textContent = activity.solution.discussion;
  content.append(explanationLabel, explanation);

  const alternatives = activity.solution.alternatives ?? [];
  if (alternatives.length > 0) {
    const alternativesLabel = document.createElement("strong");
    alternativesLabel.className = "interactive-activity__solution-heading";
    alternativesLabel.textContent = "Inne poprawne rozwiązania";
    content.append(alternativesLabel);

    for (const alternative of alternatives) {
      const alternativeElement = document.createElement("div");
      alternativeElement.className = "interactive-activity__alternative";

      const alternativeLabel = document.createElement("div");
      alternativeLabel.className = "interactive-activity__alternative-label";
      alternativeLabel.textContent = alternative.label;

      const alternativeDiscussion = document.createElement("p");
      alternativeDiscussion.className =
        "interactive-activity__discussion-text";
      alternativeDiscussion.textContent = alternative.discussion;

      alternativeElement.append(
        alternativeLabel,
        createReadonlyCodeBlock(document, alternative.code),
        alternativeDiscussion,
      );
      content.append(alternativeElement);
    }
  }

  return content;
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
    const shell = createActivityShell({
      document,
      activity,
      type: "code",
      typeLabel: "Ćwiczenie z kodem",
      title: activity.label,
      prompt: activity.prompt,
      stateAction: true,
    });

    const editorLabel = document.createElement("label");
    editorLabel.className = "interactive-activity__editor-label";
    const editorId = `${shell.promptId}-editor`;
    editorLabel.htmlFor = editorId;
    editorLabel.textContent = "Kod Python";

    const editorHelp = document.createElement("p");
    const editorHelpId = `${editorId}-help`;
    editorHelp.id = editorHelpId;
    editorHelp.className = "interactive-activity__editor-help";
    editorHelp.textContent = "Tab — wcięcie · Esc — przejście do przycisków";

    const editor = document.createElement("textarea");
    editor.id = editorId;
    editor.className = "interactive-activity__editor";
    editor.rows = 6;
    editor.spellcheck = false;
    editor.setAttribute("autocapitalize", "off");
    editor.setAttribute("autocomplete", "off");
    editor.setAttribute(
      "aria-describedby",
      `${shell.promptId} ${editorHelpId}`,
    );
    editor.value = activity.starter_code;

    const executionControls = document.createElement("div");
    executionControls.className = "interactive-activity__actions";
    executionControls.setAttribute("role", "group");
    executionControls.setAttribute(
      "aria-label",
      "Uruchamianie i sprawdzanie kodu",
    );

    const runButton = document.createElement("button");
    runButton.type = "button";
    runButton.className =
      "interactive-activity__button interactive-activity__button--primary";
    runButton.textContent = "Uruchom";

    const stopButton = document.createElement("button");
    stopButton.type = "button";
    stopButton.className = "interactive-activity__button";
    stopButton.textContent = "Zatrzymaj";
    stopButton.disabled = true;

    const resetButton = document.createElement("button");
    resetButton.type = "button";
    resetButton.className = "interactive-activity__button";
    resetButton.textContent = "Resetuj interpreter";
    resetButton.disabled = true;

    const restoreCodeButton = document.createElement("button");
    restoreCodeButton.type = "button";
    restoreCodeButton.className = "interactive-activity__button";
    restoreCodeButton.textContent = "Przywróć kod początkowy";
    restoreCodeButton.disabled = true;

    const checkButton = document.createElement("button");
    checkButton.type = "button";
    checkButton.className =
      "interactive-activity__button interactive-activity__button--primary";
    checkButton.textContent = "Sprawdź";
    checkButton.disabled = true;

    executionControls.append(runButton, stopButton, checkButton);

    const resetControls = document.createElement("div");
    resetControls.className = "interactive-activity__technical-actions";
    resetControls.setAttribute("role", "group");
    resetControls.setAttribute(
      "aria-label",
      "Operacje techniczne kodu i interpretera",
    );
    resetControls.append(restoreCodeButton, resetButton);

    const status = document.createElement("p");
    status.className = "interactive-activity__runtime-status";
    status.setAttribute("aria-live", "polite");
    status.setAttribute("aria-atomic", "true");
    status.textContent = "Interpreter nie został jeszcze uruchomiony.";

    const outputs = document.createElement("div");
    outputs.className = "interactive-activity__outputs";

    const stdoutGroup = document.createElement("div");
    stdoutGroup.className = "interactive-activity__output-group";
    const stdoutLabel = document.createElement("div");
    const stdoutLabelId = `${editorId}-stdout-label`;
    stdoutLabel.id = stdoutLabelId;
    stdoutLabel.className = "interactive-activity__output-title";
    stdoutLabel.textContent = "Standardowe wyjście (stdout)";
    const stdout = document.createElement("pre");
    stdout.className = "interactive-activity__output";
    stdout.setAttribute("aria-labelledby", stdoutLabelId);
    stdoutGroup.append(stdoutLabel, stdout);

    const stderrGroup = document.createElement("div");
    stderrGroup.className =
      "interactive-activity__output-group interactive-activity__output-group--stderr";
    const stderrLabel = document.createElement("div");
    const stderrLabelId = `${editorId}-stderr-label`;
    stderrLabel.id = stderrLabelId;
    stderrLabel.className = "interactive-activity__output-title";
    stderrLabel.textContent = "Błędy i komunikaty diagnostyczne (stderr)";
    const stderr = document.createElement("pre");
    stderr.className = "interactive-activity__output";
    stderr.setAttribute("aria-labelledby", stderrLabelId);
    stderrGroup.append(stderrLabel, stderr);
    outputs.append(stdoutGroup, stderrGroup);

    const feedback = document.createElement("p");
    feedback.className = "interactive-activity__message";
    feedback.setAttribute("aria-live", "polite");
    feedback.setAttribute("aria-atomic", "true");
    feedback.hidden = true;

    const summary = document.createElement("p");
    summary.className = "interactive-activity__meta";
    const help = createActivityHelp({
      document,
      activityId: activity.activity_id,
      solutionContent: createCodeSolutionContent(document, activity),
      discussionContent: createCodeDiscussionContent(document, activity),
    });
    executionControls.append(help.actions);
    let savedState = null;
    let hasSavedState = false;
    let progressReadFailed = false;
    let localSolutionRevealed = false;
    let localDiscussionRevealed = false;
    try {
      savedState = await store.get(activity.activity_id);
      hasSavedState = savedState !== null;
      const sourceCode = savedState?.payload?.source_code;
      if (typeof sourceCode === "string") {
        editor.value = sourceCode;
      }
      restoreFeedback(activity, savedState, feedback);
      setProgressSummary(summary, savedState);
      localSolutionRevealed =
        savedState?.payload?.solution_revealed === true
        || savedState?.payload?.discussion_revealed === true;
      localDiscussionRevealed =
        savedState?.payload?.discussion_revealed === true;
      help.restoreRevealState({
        solutionRevealed: localSolutionRevealed,
        discussionRevealed: localDiscussionRevealed,
      });
      shell.setProgressState(isCompleted(savedState) ? "completed" : "pending");
    } catch (error) {
      progressReadFailed = true;
      shell.setProgressState("unknown");
      setProgressSummary(summary, null);
      showTechnicalError(
        feedback,
        "nie można odczytać lokalnego stanu aktywności.",
      );
      console.warn("Nie udało się odczytać postępu aktywności code.", error);
    }

    let preparing = false;
    let running = false;
    let checking = false;
    let restarting = false;
    let savingCompletion = false;
    let workerAvailable = false;
    let lastExecution = null;
    let activeRunPromise = null;

    function currentHelpPayload() {
      return {
        ...(localSolutionRevealed ? { solution_revealed: true } : {}),
        ...(localDiscussionRevealed
          ? { discussion_revealed: true }
          : {}),
      };
    }

    function hasRestorableInitialState() {
      const savedSourceCode = savedState?.payload?.source_code;
      const savedSourceNeedsRestore = hasSavedState
        && typeof savedSourceCode === "string"
        && savedSourceCode !== activity.starter_code;
      const savedResultNeedsClear = hasSavedState
        && Object.prototype.hasOwnProperty.call(
          savedState?.payload ?? {},
          "last_result",
        );

      return savedSourceNeedsRestore
        || savedResultNeedsClear
        || editor.value !== activity.starter_code
        || Boolean(lastExecution)
        || workerAvailable
        || stdout.textContent !== ""
        || stderr.textContent !== ""
        || !feedback.hidden;
    }

    function updateControls() {
      const controlState = deriveCodeControlState({
        preparing,
        running,
        checking,
        restarting,
        savingCompletion,
        executionIsCurrent:
          Boolean(lastExecution)
          && lastExecution.sourceCode === editor.value,
        workerAvailable,
        activityCanRestart:
          !progressReadFailed && hasSavedState && isCompleted(savedState),
      });
      editor.disabled = controlState.editorDisabled;
      runButton.disabled = controlState.runDisabled;
      stopButton.disabled = controlState.stopDisabled;
      resetButton.disabled = controlState.resetDisabled;
      checkButton.disabled = controlState.checkDisabled;
      const busy =
        preparing || running || checking || restarting || savingCompletion;
      const completed = isCompleted(savedState);
      shell.stateActionButton.disabled = completed
        ? controlState.restartActivityDisabled
        : progressReadFailed || busy;
      restoreCodeButton.disabled = completed
        || progressReadFailed
        || preparing
        || checking
        || restarting
        || savingCompletion
        || (!running && !hasRestorableInitialState());
      help.setBusy(busy);
    }

    function invalidateExecution() {
      lastExecution = null;
      clearFeedback(feedback);
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
      if (event.key === "Escape") {
        const firstAvailableButton = [
          runButton,
          stopButton,
          checkButton,
          restoreCodeButton,
          resetButton,
          shell.stateActionButton,
        ].find((button) => !button.disabled);
        if (firstAvailableButton) {
          event.preventDefault();
          firstAvailableButton.focus();
        }
        return;
      }

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

    async function performRun() {
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
          createCodeRunProgressState(
            activity,
            currentState,
            sourceCode,
          ),
        );
        hasSavedState = true;
        setProgressSummary(summary, savedState);
        shell.setProgressState(
          isCompleted(savedState) ? "completed" : "pending",
        );
      } catch (error) {
        progressSaved = false;
        showTechnicalError(
          feedback,
          "nie udało się zapisać kodu i postępu aktywności.",
        );
        console.warn("Nie udało się zapisać postępu aktywności code.", error);
      }

      preparing = false;
      running = true;
      updateControls();
      try {
        const runtimePromise = runtime.run(sourceCode, {
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
        workerAvailable = true;
        updateControls();
        const result = await runtimePromise;
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
        workerAvailable = error?.code === "execution_error";

        if (restarting && error?.code === "reset") {
          return;
        }

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
    }

    runButton.addEventListener("click", () => {
      if (preparing || running || checking || restarting || savingCompletion) {
        return undefined;
      }

      const operation = performRun();
      const trackedOperation = operation.finally(() => {
        if (activeRunPromise === trackedOperation) {
          activeRunPromise = null;
        }
      });
      activeRunPromise = trackedOperation;
      return trackedOperation;
    });

    stopButton.addEventListener("click", () => {
      runtime.stop();
      workerAvailable = false;
      invalidateExecution();
      status.textContent = "Zatrzymywanie wykonania…";
    });

    resetButton.addEventListener("click", () => {
      if (
        !workerAvailable
        || preparing
        || checking
        || restarting
        || savingCompletion
      ) {
        return;
      }
      runtime.reset();
      workerAvailable = false;
      invalidateExecution();
      stdout.textContent = "";
      stderr.textContent = "";
      status.textContent = "Interpreter zresetowano. Następny Run załaduje go ponownie.";
    });

    async function restoreInitialState({
      clearHelp,
      alwaysResetRuntime,
      resetProgress,
      technicalError,
      warning,
      resetFailureStatus,
      failureStatus,
    }) {
      restarting = true;
      updateControls();
      const interruptedRun = activeRunPromise;
      let runtimeWasReset = false;
      let restoreSucceeded = false;

      try {
        if (
          alwaysResetRuntime
          || workerAvailable
          || running
          || interruptedRun
        ) {
          runtime.reset();
          runtimeWasReset = true;
          workerAvailable = false;
          lastExecution = null;
          updateControls();
        }

        if (interruptedRun) {
          await interruptedRun;
        }

        if (hasSavedState && resetProgress) {
          await store.reset([activity.activity_id]);
          savedState = null;
          hasSavedState = false;
        } else if (hasSavedState) {
          const currentState = await store.get(activity.activity_id);
          if (currentState === null) {
            savedState = null;
            hasSavedState = false;
          } else {
            savedState = await store.save(
              activity.activity_id,
              createCodeRunProgressState(
                activity,
                currentState,
                activity.starter_code,
              ),
            );
            hasSavedState = true;
          }
        }

        lastExecution = null;
        editor.value = activity.starter_code;
        stdout.textContent = "";
        stderr.textContent = "";
        clearFeedback(feedback);
        if (clearHelp) {
          localSolutionRevealed = false;
          localDiscussionRevealed = false;
          help.resetLocalRevealState();
        }
        setProgressSummary(summary, savedState);
        shell.setProgressState(
          isCompleted(savedState) ? "completed" : "pending",
        );
        status.textContent = "Interpreter nie został jeszcze uruchomiony.";
        restoreSucceeded = true;
      } catch (error) {
        showTechnicalError(feedback, technicalError);
        status.textContent = runtimeWasReset
          ? resetFailureStatus
          : failureStatus;
        console.warn(warning, error);
      } finally {
        restarting = false;
        updateControls();
        if (restoreSucceeded) {
          editor.focus();
        }
      }
    }

    async function restartActivity() {
      if (
        preparing
        || checking
        || restarting
        || savingCompletion
        || progressReadFailed
        || !hasSavedState
        || !isCompleted(savedState)
      ) {
        return;
      }

      await restoreInitialState({
        clearHelp: true,
        alwaysResetRuntime: true,
        resetProgress: true,
        technicalError: "nie udało się rozpocząć aktywności od nowa.",
        warning: "Nie udało się rozpocząć aktywności code od nowa.",
        resetFailureStatus:
          "Interpreter zresetowano, ale nie udało się wyzerować postępu aktywności.",
        failureStatus:
          "Nie udało się zresetować interpretera ani rozpocząć aktywności od nowa.",
      });
    }

    async function restoreStarterCode() {
      if (
        isCompleted(savedState)
        || progressReadFailed
        || preparing
        || checking
        || restarting
        || savingCompletion
        || (!running && !hasRestorableInitialState())
      ) {
        return;
      }

      await restoreInitialState({
        clearHelp: false,
        alwaysResetRuntime: false,
        resetProgress: false,
        technicalError: "nie udało się przywrócić kodu początkowego.",
        warning: "Nie udało się przywrócić kodu początkowego aktywności code.",
        resetFailureStatus:
          "Interpreter zresetowano, ale nie udało się przywrócić kodu początkowego.",
        failureStatus: "Nie udało się przywrócić kodu początkowego.",
      });
    }

    async function saveManualCompletion(completionMethod) {
      if (
        preparing
        || running
        || checking
        || restarting
        || savingCompletion
        || progressReadFailed
      ) {
        return;
      }

      savingCompletion = true;
      updateControls();
      try {
        const currentState = await store.get(activity.activity_id);
        const sourceChanged =
          editor.value !== currentState?.payload?.source_code;
        const nextState = createManualCompletionProgressState(
          activity,
          currentState,
          {
            completionMethod,
            payloadPatch: {
              source_code: editor.value,
              ...currentHelpPayload(),
            },
            removePayloadKeys: sourceChanged ? ["last_result"] : [],
          },
        );
        savedState = await store.save(activity.activity_id, nextState);
        hasSavedState = true;
        setProgressSummary(summary, savedState);
        shell.setProgressState(
          isCompleted(savedState) ? "completed" : "pending",
        );
        if (
          feedback.className.includes(
            "interactive-activity__message--error",
          )
        ) {
          clearFeedback(feedback);
        }
      } catch (error) {
        showTechnicalError(feedback, "nie udało się zapisać postępu.");
        console.warn("Nie udało się zapisać postępu aktywności code.", error);
      } finally {
        savingCompletion = false;
        updateControls();
      }
    }

    help.solutionButton.addEventListener("click", async () => {
      localSolutionRevealed = true;
      updateControls();
      if (savedState?.payload?.solution_revealed === true) {
        return;
      }
      await saveManualCompletion("solution_shown");
    });

    help.discussionButton.addEventListener("click", async () => {
      localSolutionRevealed = true;
      localDiscussionRevealed = true;
      updateControls();
      if (savedState?.payload?.discussion_revealed === true) {
        return;
      }
      await saveManualCompletion("solution_shown");
    });

    restoreCodeButton.addEventListener("click", () => restoreStarterCode());

    shell.stateActionButton.addEventListener("click", async () => {
      if (
        preparing
        || checking
        || restarting
        || savingCompletion
        || progressReadFailed
      ) {
        return;
      }

      if (isCompleted(savedState)) {
        await restartActivity();
        return;
      }

      if (running) {
        return;
      }
      await saveManualCompletion("self_marked");
      if (isCompleted(savedState)) {
        shell.stateActionButton.focus?.();
      }
    });

    checkButton.addEventListener("click", async () => {
      if (
        checking
        || restarting
        || savingCompletion
        || !lastExecution
        || lastExecution.sourceCode !== editor.value
      ) {
        return;
      }

      checking = true;
      try {
        updateControls();

        let isCorrect;
        try {
          isCorrect = checkCodeResult(activity, lastExecution);
        } catch (error) {
          showTechnicalError(
            feedback,
            "nie można sprawdzić rozwiązania z powodu błędu konfiguracji aktywności.",
          );
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
          hasSavedState = true;
          showFeedback(activity, nextState.payload.last_result, feedback);
          setProgressSummary(summary, savedState);
          shell.setProgressState(
            isCompleted(savedState) ? "completed" : "pending",
          );
        } catch (error) {
          showTechnicalError(
            feedback,
            "nie udało się zapisać wyniku sprawdzenia.",
          );
          console.warn("Nie udało się zapisać postępu aktywności code.", error);
        }
      } finally {
        checking = false;
        updateControls();
      }
    });

    updateControls();

    shell.interaction.append(
      editorLabel,
      editorHelp,
      editor,
      executionControls,
      resetControls,
      help.panels,
      outputs,
    );
    shell.messages.append(status, feedback, summary);
    return shell.root;
  };
}
