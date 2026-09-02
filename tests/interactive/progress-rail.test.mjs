import assert from "node:assert/strict";
import test from "node:test";

import {
  createProgressRail,
  deriveCompletionProgress,
  insertProgressRail,
  updateProgressRail,
} from "../../docs/javascripts/interactive/progress-rail.js";
import { createFakeDocument } from "./support/fake-dom.mjs";


test("wylicza cztery stany bez przechowywania statusów", () => {
  const states = new Map([
    ["first", false],
    ["second", false],
  ]);
  const getCompletion = (activityId) => states.get(activityId);

  assert.deepEqual(
    deriveCompletionProgress([], getCompletion),
    { completed: 0, state: "none", total: 0 },
  );
  assert.deepEqual(
    deriveCompletionProgress(["first", "first", "second"], getCompletion),
    { completed: 0, state: "none_completed", total: 2 },
  );

  states.set("first", true);
  assert.deepEqual(
    deriveCompletionProgress(["first", "second"], getCompletion),
    { completed: 1, state: "partial", total: 2 },
  );

  states.set("second", true);
  assert.deepEqual(
    deriveCompletionProgress(["first", "second"], getCompletion),
    { completed: 2, state: "completed", total: 2 },
  );
  assert.equal(deriveCompletionProgress(["missing"], getCompletion), null);
});


test("tworzy dostępny rail strony bez nowego punktu Tab i aria-live", () => {
  const document = createFakeDocument();
  const marker = createProgressRail({
    document,
    kind: "page",
    progress: { completed: 1, state: "partial", total: 2 },
  });

  assert.equal(marker.hasAttribute("data-interactive-page-progress"), true);
  assert.equal(marker.getAttribute("data-state"), "partial");
  assert.equal(
    marker.className,
    "interactive-progress-rail interactive-progress-rail--page "
      + "interactive-progress-rail--partial",
  );
  assert.equal(
    marker.getAttribute("title"),
    "Ćwiczenia na tej stronie: ukończono 1 z 2.",
  );
  assert.equal(marker.hasAttribute("tabindex"), false);
  assert.equal(marker.hasAttribute("aria-live"), false);
  assert.equal(marker.children[0].className, "interactive-progress-rail__visual");
  assert.equal(marker.children[0].getAttribute("aria-hidden"), "true");
  assert.equal(
    marker.children[1].className,
    "interactive-activity__visually-hidden",
  );
  assert.equal(
    marker.children[1].textContent,
    "Ćwiczenia na tej stronie: ukończono 1 z 2.",
  );
});


test("wstawia osobny marker po etykiecie bez zmiany linku Material", () => {
  const document = createFakeDocument();
  const link = document.createElement("a");
  link.className = "md-nav__link md-nav__link--active";
  link.setAttribute("href", "../strona/");
  link.setAttribute("style", "border-left: 3px solid blue");
  const label = document.createElement("span");
  label.className = "md-ellipsis";
  label.textContent = "Strona";
  link.append(label);

  const marker = createProgressRail({
    document,
    kind: "page",
    progress: { completed: 0, state: "none", total: 0 },
  });
  assert.equal(insertProgressRail(link, marker), true);

  assert.equal(link.children[0], label);
  assert.equal(link.children[1], marker);
  assert.equal(link.getAttribute("href"), "../strona/");
  assert.equal(link.className, "md-nav__link md-nav__link--active");
  assert.equal(link.getAttribute("style"), "border-left: 3px solid blue");
  assert.equal(
    marker.getAttribute("title"),
    "Do tej strony nie przypisano ćwiczeń.",
  );
});


test("aktualizuje wyłącznie własny DOM raila", () => {
  const document = createFakeDocument();
  const marker = createProgressRail({
    document,
    kind: "section",
    progress: { completed: 0, state: "none_completed", total: 2 },
  });

  updateProgressRail(marker, {
    kind: "section",
    progress: { completed: 2, state: "completed", total: 2 },
  });

  assert.equal(marker.getAttribute("data-state"), "completed");
  assert.equal(
    marker.className,
    "interactive-progress-rail interactive-progress-rail--section "
      + "interactive-progress-rail--completed",
  );
  assert.equal(
    marker.children[1].textContent,
    "Ćwiczenia w tej sekcji: ukończono 2 z 2.",
  );
});
