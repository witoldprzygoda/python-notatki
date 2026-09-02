import assert from "node:assert/strict";
import test from "node:test";

import { ActivityEngine } from "../../docs/javascripts/interactive/activity-engine.js";
import {
  createFakeDocument,
  hasClass,
} from "./support/fake-dom.mjs";


function createRootWithSlot(document, slotId) {
  const slot = document.createElement("div");
  slot.dataset.activitySlot = slotId;
  return {
    slot,
    root: {
      querySelectorAll(selector) {
        assert.equal(selector, "[data-activity-slot]");
        return [slot];
      },
    },
  };
}


function createRenderer(callOrder) {
  return async ({ activity, document }) => {
    callOrder.push(activity.activity_id);
    const element = document.createElement("section");
    element.textContent = activity.activity_id;
    return element;
  };
}


test("grupuje aktywności slotu w jednym domyślnie zamkniętym details", async () => {
  const document = createFakeDocument();
  const { root, slot } = createRootWithSlot(document, "page-activities");
  const callOrder = [];
  const engine = new ActivityEngine({
    store: {},
    renderers: new Map([["single_choice", createRenderer(callOrder)]]),
  });

  await engine.render(root, [
    {
      activity_id: "first",
      slot_id: "page-activities",
      type: "single_choice",
    },
    {
      activity_id: "second",
      slot_id: "page-activities",
      type: "single_choice",
    },
  ]);

  assert.deepEqual(callOrder, ["first", "second"]);
  assert.equal(slot.children.length, 1);
  const details = slot.children[0];
  assert.equal(details.tagName, "details");
  assert.equal(details.hasAttribute("open"), false);
  assert.equal(details.children[0].tagName, "summary");
  assert.equal(details.children[0].textContent, "Ćwiczenia i pytania");
  assert.equal(hasClass(details.children[1], "interactive-activity-group__content"), true);
  assert.deepEqual(
    details.children[1].children.map((element) => element.textContent),
    ["first", "second"],
  );
});


test("nie opakowuje ponownie tego samego slotu", async () => {
  const document = createFakeDocument();
  const { root, slot } = createRootWithSlot(document, "page-activities");
  const callOrder = [];
  const engine = new ActivityEngine({
    store: {},
    renderers: new Map([["code", createRenderer(callOrder)]]),
  });
  const activities = [
    { activity_id: "code", slot_id: "page-activities", type: "code" },
  ];

  await engine.render(root, activities);
  const details = slot.children[0];
  details.setAttribute("open", "");
  await engine.render(root, activities);

  assert.deepEqual(callOrder, ["code"]);
  assert.equal(slot.children[0], details);
  assert.equal(details.hasAttribute("open"), true);
});


test("renderuje nowy slot po navigation.instant bez duplikacji", async () => {
  const document = createFakeDocument();
  const firstPage = createRootWithSlot(document, "page-activities");
  const secondPage = createRootWithSlot(document, "page-activities");
  const callOrder = [];
  const engine = new ActivityEngine({
    store: {},
    renderers: new Map([["code", createRenderer(callOrder)]]),
  });
  const activities = [
    { activity_id: "code", slot_id: "page-activities", type: "code" },
  ];

  await engine.render(firstPage.root, activities);
  await engine.render(secondPage.root, activities);

  assert.deepEqual(callOrder, ["code", "code"]);
  assert.equal(firstPage.slot.children.length, 1);
  assert.equal(secondPage.slot.children.length, 1);
  assert.equal(secondPage.slot.children[0].hasAttribute("open"), false);
});
