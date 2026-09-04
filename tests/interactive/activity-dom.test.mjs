import assert from "node:assert/strict";
import test from "node:test";

import {
  createActivityShell,
} from "../../docs/javascripts/interactive/activity-dom.js";
import {
  createFakeDocument,
  findByClass,
  hasClass,
} from "./support/fake-dom.mjs";


test("tworzy wspólną, opisaną powłokę w stałej kolejności", () => {
  const document = createFakeDocument();
  const shell = createActivityShell({
    document,
    activity: { activity_id: "flow-for-quiz-001" },
    type: "single-choice",
    typeLabel: "Pytanie jednokrotnego wyboru",
    title: "Sprawdzenie pętli",
    prompt: "Wybierz odpowiedź.",
  });

  assert.equal(shell.root.tagName, "section");
  assert.equal(hasClass(shell.root, "interactive-activity"), true);
  assert.equal(
    hasClass(shell.root, "interactive-activity--single-choice"),
    true,
  );
  assert.equal(shell.root.dataset.activityId, "flow-for-quiz-001");
  assert.equal(shell.root.dataset.activityType, "single-choice");
  assert.equal(shell.root.dataset.progressState, "pending");
  assert.equal(shell.title.tagName, "div");
  assert.equal(shell.root.getAttribute("aria-labelledby"), shell.title.id);

  const header = findByClass(shell.root, "interactive-activity__header");
  assert.deepEqual(shell.root.children, [header, shell.body]);
  assert.deepEqual(
    shell.body.children,
    [shell.prompt, shell.interaction, shell.messages],
  );
  assert.equal(shell.prompt.id, shell.promptId);
  assert.equal(shell.progress.getAttribute("aria-live"), null);
  assert.equal(shell.progress.textContent, "○ Do wykonania");
  assert.equal(shell.stateActionButton, null);
});


test("tworzy jeden stanowy przycisk nagłówka przed wskaźnikiem", () => {
  const document = createFakeDocument();
  const shell = createActivityShell({
    document,
    activity: { activity_id: "flow-for-code-001" },
    type: "code",
    typeLabel: "Ćwiczenie z kodem",
    title: "Praca z pętlą",
    prompt: "Uzupełnij kod.",
    stateAction: true,
  });

  const headerState = findByClass(
    shell.root,
    "interactive-activity__header-state",
  );
  const stateActionButton = shell.stateActionButton;

  assert.ok(headerState);
  assert.ok(stateActionButton);
  assert.equal(stateActionButton.tagName, "button");
  assert.equal(stateActionButton.getAttribute("type"), "button");
  assert.equal(
    hasClass(stateActionButton, "interactive-activity__header-control"),
    true,
  );
  assert.equal(
    hasClass(shell.progress, "interactive-activity__header-control"),
    true,
  );
  assert.deepEqual(headerState.children, [stateActionButton, shell.progress]);
  assert.equal(stateActionButton.textContent, "Oznacz jako wykonane");
  assert.equal(shell.progress.textContent, "○ Do wykonania");

  shell.setProgressState("completed");
  assert.equal(shell.stateActionButton, stateActionButton);
  assert.equal(stateActionButton.textContent, "Zacznij od nowa");
  assert.equal(shell.progress.textContent, "✓ Wykonano");

  shell.setProgressState("unknown");
  assert.equal(shell.stateActionButton, stateActionButton);
  assert.equal(stateActionButton.textContent, "Oznacz jako wykonane");
  assert.equal(shell.progress.textContent, "— Stan niedostępny");
});


test("renderuje tytuł i polecenie jako literalny textContent", () => {
  const document = createFakeDocument();
  const title = "Tytuł <img src=x onerror=alert(1)>";
  const prompt = "Polecenie <script>alert(1)</script>";
  const shell = createActivityShell({
    document,
    activity: { activity_id: "literal-text-001" },
    type: "code",
    typeLabel: "Ćwiczenie z kodem",
    title,
    prompt,
  });

  assert.equal(shell.title.textContent, title);
  assert.equal(shell.title.children.length, 0);
  assert.equal(shell.prompt.textContent, `Polecenie: ${prompt}`);
  assert.equal(
    shell.prompt.children.some((element) => element.tagName === "script"),
    false,
  );

  shell.setProgressState("completed");
  assert.equal(shell.root.dataset.progressState, "completed");
  assert.equal(shell.progress.textContent, "✓ Wykonano");
  assert.equal(
    shell.root.children[0].children.filter(
      (element) => hasClass(element, "interactive-activity__progress"),
    ).length,
    1,
  );
});


test("generuje różne identyfikatory DOM dla różnych activity_id", () => {
  const document = createFakeDocument();
  const createShell = (activityId) => createActivityShell({
    document,
    activity: { activity_id: activityId },
    type: "acknowledgement",
    typeLabel: "Potwierdzenie",
    title: "Tytuł",
    prompt: "Polecenie.",
  });

  const encoded = createShell("a/b");
  const literal = createShell("a-2Fb");

  assert.notEqual(encoded.title.id, literal.title.id);
  assert.equal(encoded.root.getAttribute("aria-labelledby"), encoded.title.id);
  assert.equal(literal.root.getAttribute("aria-labelledby"), literal.title.id);
});
