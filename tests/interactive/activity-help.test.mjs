import assert from "node:assert/strict";
import test from "node:test";

import {
  createActivityHelp,
} from "../../docs/javascripts/interactive/activity-help.js";
import {
  createFakeDocument,
  dispatch,
  findByClass,
} from "./support/fake-dom.mjs";


function createHelp(activityId = "flow-for-code-001") {
  const document = createFakeDocument();
  const solutionContent = document.createElement("pre");
  solutionContent.textContent = "print('<solution>')";
  const discussionContent = document.createElement("p");
  discussionContent.textContent = "Porównaj <wynik> z poleceniem.";

  return {
    document,
    solutionContent,
    discussionContent,
    help: createActivityHelp({
      document,
      activityId,
      solutionContent,
      discussionContent,
    }),
  };
}


test("tworzy opisaną grupę rozwiązania i osobny kontener paneli", () => {
  const { help, solutionContent, discussionContent } = createHelp();
  const label = findByClass(
    help.actions,
    "interactive-activity__solution-label",
  );

  assert.equal(help.actions.getAttribute("role"), "group");
  assert.equal(help.actions.getAttribute("aria-labelledby"), label.id);
  assert.equal(label.textContent, "Rozwiązanie:");
  assert.equal(
    findByClass(help.actions, "interactive-activity__help-heading"),
    undefined,
  );
  assert.equal(help.panels.className, "interactive-activity__help-panels");

  assert.equal(help.solutionButton.tagName, "button");
  assert.equal(help.solutionButton.getAttribute("type"), "button");
  assert.equal(help.solutionButton.textContent, "Pokaż");
  assert.equal(
    help.solutionButton.getAttribute("aria-label"),
    "Pokaż rozwiązanie",
  );
  assert.equal(help.solutionButton.getAttribute("aria-expanded"), "false");
  assert.equal(
    help.solutionButton.getAttribute("aria-controls"),
    help.solutionPanel.id,
  );
  assert.equal(help.solutionPanel.getAttribute("role"), "region");
  assert.equal(
    help.solutionPanel.getAttribute("aria-labelledby"),
    help.solutionButton.id,
  );
  assert.equal(help.solutionPanel.getAttribute("tabindex"), "-1");
  assert.equal(help.solutionPanel.hidden, true);

  assert.equal(help.discussionButton.getAttribute("type"), "button");
  assert.equal(help.discussionButton.textContent, "Omów");
  assert.equal(
    help.discussionButton.getAttribute("aria-label"),
    "Omów rozwiązanie",
  );
  assert.equal(help.discussionButton.getAttribute("aria-expanded"), "false");
  assert.equal(
    help.discussionButton.getAttribute("aria-controls"),
    help.discussionPanel.id,
  );
  assert.equal(help.discussionPanel.hidden, true);

  assert.deepEqual(
    help.actions.children,
    [label, help.solutionButton, help.discussionButton],
  );
  assert.deepEqual(
    help.panels.children,
    [help.solutionPanel, help.discussionPanel],
  );
  assert.equal(solutionContent.parentNode, help.solutionPanel);
  assert.equal(discussionContent.parentNode, help.discussionPanel);
});


test("odsłania rozwiązanie jednokierunkowo i skupia tylko nowy panel", async () => {
  const { help } = createHelp();
  let focusCount = 0;
  help.solutionPanel.focus = () => {
    focusCount += 1;
  };

  await dispatch(help.solutionButton, "click");
  await dispatch(help.solutionButton, "click");

  assert.equal(help.solutionPanel.hidden, false);
  assert.equal(help.solutionButton.getAttribute("aria-expanded"), "true");
  assert.equal(focusCount, 1);
});


test("omówienie odsłania także rozwiązanie", async () => {
  const { help } = createHelp();
  let solutionFocusCount = 0;
  let discussionFocusCount = 0;
  help.solutionPanel.focus = () => {
    solutionFocusCount += 1;
  };
  help.discussionPanel.focus = () => {
    discussionFocusCount += 1;
  };

  await dispatch(help.discussionButton, "click");

  assert.equal(help.solutionPanel.hidden, false);
  assert.equal(help.discussionPanel.hidden, false);
  assert.equal(help.solutionButton.getAttribute("aria-expanded"), "true");
  assert.equal(help.discussionButton.getAttribute("aria-expanded"), "true");
  assert.equal(solutionFocusCount, 0);
  assert.equal(discussionFocusCount, 1);
});


test("odtwarza flagi bez zwijania odsłoniętej treści", () => {
  const { help } = createHelp();

  help.restoreRevealState({ discussionRevealed: true });
  help.restoreRevealState({
    solutionRevealed: false,
    discussionRevealed: false,
  });

  assert.equal(help.solutionPanel.hidden, false);
  assert.equal(help.discussionPanel.hidden, false);
  assert.equal(help.solutionButton.getAttribute("aria-expanded"), "true");
  assert.equal(help.discussionButton.getAttribute("aria-expanded"), "true");
});


test("resetuje wyłącznie lokalny stan odsłonięcia", () => {
  const { help } = createHelp();
  help.restoreRevealState({ discussionRevealed: true });

  help.resetLocalRevealState();

  assert.equal(help.solutionPanel.hidden, true);
  assert.equal(help.discussionPanel.hidden, true);
  assert.equal(help.solutionButton.getAttribute("aria-expanded"), "false");
  assert.equal(help.discussionButton.getAttribute("aria-expanded"), "false");
});


test("stan busy wyłącza wyłącznie akcje ujawniania", () => {
  const { help } = createHelp();

  help.setBusy(true);
  assert.equal(help.solutionButton.disabled, true);
  assert.equal(help.discussionButton.disabled, true);

  help.setBusy(false);
  assert.equal(help.solutionButton.disabled, false);
  assert.equal(help.discussionButton.disabled, false);
});


test("generuje unikalne identyfikatory z activity_id", () => {
  const first = createHelp("flow/a").help;
  const second = createHelp("flow-2Fa").help;

  assert.notEqual(first.solutionPanel.id, second.solutionPanel.id);
  assert.notEqual(first.discussionPanel.id, second.discussionPanel.id);
  assert.equal(
    first.solutionButton.getAttribute("aria-controls"),
    first.solutionPanel.id,
  );
  assert.equal(
    second.discussionButton.getAttribute("aria-controls"),
    second.discussionPanel.id,
  );
});


test("zachowuje przekazane węzły i ich literalną treść", () => {
  const { help, solutionContent, discussionContent } = createHelp();

  assert.equal(help.solutionPanel.children[0], solutionContent);
  assert.equal(help.discussionPanel.children[0], discussionContent);
  assert.equal(help.solutionPanel.textContent, "print('<solution>')");
  assert.equal(
    help.discussionPanel.textContent,
    "Porównaj <wynik> z poleceniem.",
  );
  assert.equal(help.solutionPanel.children.length, 1);
  assert.equal(help.discussionPanel.children.length, 1);
});
