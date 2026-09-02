import assert from "node:assert/strict";
import test from "node:test";

import { renderSingleChoice } from "../../docs/javascripts/interactive/activities/single-choice.js";
import { createGlobalProgressController } from "../../docs/javascripts/interactive/global-progress.js";
import { NotifyingProgressStore } from "../../docs/javascripts/interactive/notifying-progress-store.js";
import {
  createSectionProgressController,
  deriveSectionProgress,
  sectionIdFromHref,
} from "../../docs/javascripts/interactive/section-progress.js";


class FakeElement {
  constructor(tagName, ownerDocument) {
    this.tagName = String(tagName).toLowerCase();
    this.ownerDocument = ownerDocument;
    this.parentNode = null;
    this.childNodes = [];
    this.attributes = new Map();
    this.className = "";
    this.dataset = {};
    this.id = "";
    this.listeners = new Map();
    this._textContent = "";
  }

  get children() {
    return this.childNodes;
  }

  get nextSibling() {
    if (!this.parentNode) {
      return null;
    }
    const index = this.parentNode.childNodes.indexOf(this);
    return this.parentNode.childNodes[index + 1] ?? null;
  }

  get textContent() {
    return this._textContent
      + this.childNodes.map((child) => child.textContent).join("");
  }

  set textContent(value) {
    this.replaceChildren();
    this._textContent = String(value);
  }

  after(node) {
    this.parentNode?.insertBefore(node, this.nextSibling);
  }

  addEventListener(type, listener) {
    const listeners = this.listeners.get(type) ?? [];
    listeners.push(listener);
    this.listeners.set(type, listeners);
  }

  append(...nodes) {
    for (const node of nodes) {
      node.parentNode?.removeChild(node);
      node.parentNode = this;
      this.childNodes.push(node);
    }
  }

  before(node) {
    this.parentNode?.insertBefore(node, this);
  }

  getAttribute(name) {
    if (name === "class") {
      return this.className || null;
    }
    if (name === "id") {
      return this.id || null;
    }
    return this.attributes.get(name) ?? null;
  }

  hasAttribute(name) {
    return this.getAttribute(name) !== null;
  }

  insertBefore(node, referenceNode) {
    node.parentNode?.removeChild(node);
    const index = referenceNode === null
      ? -1
      : this.childNodes.indexOf(referenceNode);
    node.parentNode = this;
    if (index === -1) {
      this.childNodes.push(node);
    } else {
      this.childNodes.splice(index, 0, node);
    }
    return node;
  }

  prepend(node) {
    this.insertBefore(node, this.childNodes[0] ?? null);
  }

  querySelector(selector) {
    return this.querySelectorAll(selector)[0] ?? null;
  }

  querySelectorAll(selector) {
    return allElements(this).slice(1).filter(
      (element) => matches(element, selector),
    );
  }

  remove() {
    this.parentNode?.removeChild(this);
  }

  removeChild(node) {
    const index = this.childNodes.indexOf(node);
    if (index !== -1) {
      this.childNodes.splice(index, 1);
      node.parentNode = null;
    }
    return node;
  }

  replaceChildren(...nodes) {
    for (const child of this.childNodes) {
      child.parentNode = null;
    }
    this.childNodes = [];
    this._textContent = "";
    this.append(...nodes);
  }

  setAttribute(name, value) {
    const stringValue = String(value);
    if (name === "class") {
      this.className = stringValue;
    } else if (name === "id") {
      this.id = stringValue;
    } else {
      this.attributes.set(name, stringValue);
    }
  }
}


function allElements(root) {
  return [root, ...root.children.flatMap(allElements)];
}


function matches(element, selector) {
  if (selector.startsWith(".")) {
    return element.className.split(/\s+/).includes(selector.slice(1));
  }
  const attribute = selector.match(/^\[([^=\]]+)(?:="([^"]*)")?\]$/);
  if (!attribute) {
    return false;
  }
  const [, name, expectedValue] = attribute;
  if (!element.hasAttribute(name)) {
    return false;
  }
  return expectedValue === undefined
    || element.getAttribute(name) === expectedValue;
}


function createDocument() {
  const document = {
    baseURI: "https://example.test/course/page/",
    createElement(tagName) {
      return new FakeElement(tagName, document);
    },
    querySelector(selector) {
      return document.querySelectorAll(selector)[0] ?? null;
    },
    querySelectorAll(selector) {
      return allElements(document.body).filter(
        (element) => matches(element, selector),
      );
    },
  };
  document.body = document.createElement("body");
  const container = document.createElement("div");
  container.setAttribute("data-md-component", "container");
  document.body.append(container);
  return { container, document };
}


function appendMarkedSection(document, container, sectionId) {
  const heading = document.createElement("h2");
  heading.id = sectionId;
  heading.setAttribute("data-activity-section", "true");
  container.append(heading);
  return heading;
}


function appendSlot(document, container, slotId) {
  const slot = document.createElement("div");
  slot.setAttribute("data-activity-slot", slotId);
  container.append(slot);
  return slot;
}


function appendTocLink(
  document,
  container,
  href,
  { ellipsis = true, tail = false } = {},
) {
  const toc = document.createElement("ul");
  toc.setAttribute("data-md-component", "toc");
  const link = document.createElement("a");
  link.className = "md-nav__link md-nav__link--active";
  link.setAttribute("href", href);
  if (ellipsis) {
    const label = document.createElement("span");
    label.className = "md-ellipsis";
    label.textContent = "Sekcja";
    link.append(label);
  }
  if (tail) {
    const trailing = document.createElement("span");
    trailing.className = "existing-tail";
    link.append(trailing);
  }
  toc.append(link);
  container.append(toc);
  return link;
}


function markers(document) {
  return document.querySelectorAll("[data-interactive-section-progress]");
}


function markerState(marker) {
  return marker.getAttribute("data-state");
}


async function dispatch(element, type, event = {}) {
  for (const listener of element.listeners.get(type) ?? []) {
    await listener(event);
  }
}


function activity(activityId, slotId, sectionId) {
  return { activity_id: activityId, slot_id: slotId, section_id: sectionId };
}


class CompletionSource {
  constructor(states = {}) {
    this.states = new Map(Object.entries(states));
    this.listeners = new Set();
    this.available = true;
  }

  getActivityCompletion(activityId) {
    if (!this.available) {
      return undefined;
    }
    return this.states.get(activityId) ?? false;
  }

  subscribeActivityCompletion(listener) {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  set(activityId, completed) {
    this.states.set(activityId, completed);
    this.emit([activityId]);
  }

  emit(activityIds) {
    for (const listener of [...this.listeners]) {
      listener({ activityIds });
    }
  }
}


class MemoryProgressStore {
  constructor(states = {}) {
    this.states = new Map(Object.entries(states));
    this.getCalls = [];
  }

  async get(activityId) {
    this.getCalls.push(activityId);
    const state = this.states.get(activityId);
    return state ? { ...state } : null;
  }

  async save(activityId, state) {
    const savedState = { activity_id: activityId, ...state };
    this.states.set(activityId, savedState);
    return { ...savedState };
  }

  async getSummary() {
    return { completed: 0, total: this.states.size };
  }

  async reset(activityIds = null) {
    if (activityIds === null) {
      this.states.clear();
      return;
    }
    for (const activityId of activityIds) {
      this.states.delete(activityId);
    }
  }
}


test("wylicza cztery stany sekcji i odrzuca niedostępny status", () => {
  const states = new Map([
    ["first", false],
    ["second", false],
  ]);
  const getCompletion = (activityId) => states.get(activityId);

  assert.equal(deriveSectionProgress([], getCompletion).state, "none");
  assert.equal(
    deriveSectionProgress(["first", "second"], getCompletion).state,
    "none_completed",
  );
  states.set("first", true);
  assert.equal(
    deriveSectionProgress(["first", "second"], getCompletion).state,
    "partial",
  );
  states.set("second", true);
  assert.equal(
    deriveSectionProgress(["first", "second"], getCompletion).state,
    "completed",
  );
  assert.equal(deriveSectionProgress(["missing"], getCompletion), null);
});


test("normalizuje #id, ./#id i pełny URL oraz dekoduje fragment", () => {
  const baseURI = "https://example.test/course/page/";

  assert.equal(sectionIdFromHref("#petla-for", baseURI), "petla-for");
  assert.equal(sectionIdFromHref("./#petla%2Dfor", baseURI), "petla-for");
  assert.equal(
    sectionIdFromHref(
      "https://example.test/course/page/#petla-for",
      baseURI,
    ),
    "petla-for",
  );
  assert.equal(sectionIdFromHref("#za%C5%BC%C3%B3%C5%82%C4%87", baseURI), "zażółć");
  assert.equal(sectionIdFromHref("#%E0%A4%A", baseURI), null);
  assert.equal(sectionIdFromHref("#", baseURI), null);
});


test("dekoruje obie kopie ToC bez zmiany href i klas linków", () => {
  const { container, document } = createDocument();
  appendMarkedSection(document, container, "petla-for");
  appendSlot(document, container, "page-slot");
  const firstLink = appendTocLink(
    document,
    container,
    "#petla-for",
    { tail: true },
  );
  const secondLink = appendTocLink(
    document,
    container,
    "./#petla%2Dfor",
    { ellipsis: false },
  );
  const completionSource = new CompletionSource({
    first: true,
    second: false,
  });
  const controller = createSectionProgressController({
    document,
    manifest: {
      activities: [
        activity("first", "page-slot", "petla-for"),
        activity("second", "page-slot", "petla-for"),
      ],
    },
    completionSource,
  });
  const firstHref = firstLink.getAttribute("href");
  const firstClass = firstLink.className;

  assert.equal(controller.decorateCurrentPage(), 2);

  assert.equal(markers(document).length, 2);
  assert.equal(firstLink.getAttribute("href"), firstHref);
  assert.equal(firstLink.className, firstClass);
  assert.equal(firstLink.children[1].hasAttribute("data-interactive-section-progress"), true);
  assert.equal(firstLink.children[2].className, "existing-tail");
  assert.equal(secondLink.children.at(-1).hasAttribute("data-interactive-section-progress"), true);

  for (const marker of markers(document)) {
    assert.equal(markerState(marker), "partial");
    assert.equal(
      marker.children[0].className,
      "interactive-progress-rail__visual",
    );
    assert.equal(marker.children[0].textContent, "");
    assert.equal(marker.children[0].getAttribute("aria-hidden"), "true");
    assert.equal(
      marker.children[1].className,
      "interactive-activity__visually-hidden",
    );
    assert.equal(
      marker.children[1].textContent,
      "Ćwiczenia w tej sekcji: ukończono 1 z 2.",
    );
    assert.equal(
      marker.getAttribute("title"),
      "Ćwiczenia w tej sekcji: ukończono 1 z 2.",
    );
    assert.equal(marker.hasAttribute("tabindex"), false);
    assert.equal(marker.hasAttribute("aria-live"), false);
  }
});


test("strona bez slotu dekoruje oznaczone sekcje stanem none", () => {
  const { container, document } = createDocument();
  appendMarkedSection(document, container, "bez-cwiczen");
  appendTocLink(document, container, "#bez-cwiczen");
  appendTocLink(document, container, "./#bez-cwiczen");
  const completionSource = new CompletionSource({ other: true });
  const controller = createSectionProgressController({
    document,
    manifest: {
      activities: [activity("other", "other-slot", "bez-cwiczen")],
    },
    completionSource,
  });

  assert.equal(controller.decorateCurrentPage(), 2);
  assert.deepEqual(markers(document).map(markerState), ["none", "none"]);
  assert.deepEqual(
    markers(document).map((marker) => marker.children[0].className),
    ["interactive-progress-rail__visual", "interactive-progress-rail__visual"],
  );
});


test("niedostępny model usuwa markery zamiast pokazywać fałszywy stan", () => {
  const { container, document } = createDocument();
  appendMarkedSection(document, container, "sekcja");
  appendSlot(document, container, "page-slot");
  appendTocLink(document, container, "#sekcja");
  const completionSource = new CompletionSource({ first: false });
  const controller = createSectionProgressController({
    document,
    manifest: {
      activities: [activity("first", "page-slot", "sekcja")],
    },
    completionSource,
  });

  assert.equal(controller.decorateCurrentPage(), 1);
  assert.equal(markerState(markers(document)[0]), "none_completed");

  completionSource.available = false;
  assert.equal(controller.decorateCurrentPage(), 0);
  assert.equal(markers(document).length, 0);
});


test("wielokrotne dekorowanie nie tworzy duplikatów", () => {
  const { container, document } = createDocument();
  appendMarkedSection(document, container, "sekcja");
  appendTocLink(document, container, "#sekcja");
  appendTocLink(document, container, "./#sekcja");
  const completionSource = new CompletionSource();
  const controller = createSectionProgressController({
    document,
    manifest: { activities: [] },
    completionSource,
  });

  controller.decorateCurrentPage();
  controller.decorateCurrentPage();
  controller.decorateCurrentPage();

  assert.equal(markers(document).length, 2);
});


test("zagnieżdżone rooty ToC nie dublują markera tego samego linku", () => {
  const { container, document } = createDocument();
  appendMarkedSection(document, container, "sekcja");
  const outerToc = document.createElement("nav");
  outerToc.setAttribute("data-md-component", "toc");
  const innerToc = document.createElement("nav");
  innerToc.setAttribute("data-md-component", "toc");
  const link = document.createElement("a");
  link.setAttribute("href", "#sekcja");
  innerToc.append(link);
  outerToc.append(innerToc);
  container.append(outerToc);
  const controller = createSectionProgressController({
    document,
    manifest: { activities: [] },
    completionSource: new CompletionSource(),
  });

  assert.equal(controller.decorateCurrentPage(), 1);
  assert.equal(markers(document).length, 1);
});


test("ten sam section_id jest izolowany przez slot bieżącej strony", () => {
  const { container, document } = createDocument();
  appendMarkedSection(document, container, "wspolna-sekcja");
  const slot = appendSlot(document, container, "first-slot");
  appendTocLink(document, container, "#wspolna-sekcja");
  const controller = createSectionProgressController({
    document,
    manifest: {
      activities: [
        activity("first", "first-slot", "wspolna-sekcja"),
        activity("second", "second-slot", "wspolna-sekcja"),
      ],
    },
    completionSource: new CompletionSource({ first: true, second: false }),
  });

  controller.decorateCurrentPage();
  assert.equal(markerState(markers(document)[0]), "completed");

  slot.setAttribute("data-activity-slot", "second-slot");
  controller.decorateCurrentPage();
  assert.equal(markers(document).length, 1);
  assert.equal(markerState(markers(document)[0]), "none_completed");
});


test("brak lokalnego ToC jest bezpiecznym no-opem", () => {
  const { container, document } = createDocument();
  appendMarkedSection(document, container, "sekcja");
  appendSlot(document, container, "page-slot");
  const completionSource = new CompletionSource({ first: false });
  const controller = createSectionProgressController({
    document,
    manifest: {
      activities: [activity("first", "page-slot", "sekcja")],
    },
    completionSource,
  });

  assert.equal(controller.decorateCurrentPage(), 0);
  assert.equal(markers(document).length, 0);
});


test("save i reset aktualizują natychmiast none_completed → partial → completed bez pełnych odczytów", async () => {
  const { container, document } = createDocument();
  appendMarkedSection(document, container, "sekcja");
  appendSlot(document, container, "page-slot");
  appendTocLink(document, container, "#sekcja");
  appendTocLink(document, container, "./#sekcja");
  const manifest = {
    activities: [
      activity("first", "page-slot", "sekcja"),
      activity("second", "page-slot", "sekcja"),
    ],
  };
  const delegate = new MemoryProgressStore();
  const store = new NotifyingProgressStore(delegate);
  const globalProgress = createGlobalProgressController({
    document,
    manifest,
    store,
  });
  await globalProgress.ready;
  const sectionProgress = createSectionProgressController({
    document,
    manifest,
    completionSource: globalProgress,
  });
  sectionProgress.decorateCurrentPage();
  delegate.getCalls.length = 0;

  assert.deepEqual(markers(document).map(markerState), [
    "none_completed",
    "none_completed",
  ]);

  await store.save("first", { version: 1, status: "completed" });
  await globalProgress.whenIdle();
  assert.deepEqual(markers(document).map(markerState), ["partial", "partial"]);
  assert.deepEqual(delegate.getCalls, ["first"]);

  delegate.getCalls.length = 0;
  await store.save("second", { version: 1, status: "completed" });
  await globalProgress.whenIdle();
  assert.deepEqual(markers(document).map(markerState), [
    "completed",
    "completed",
  ]);
  assert.deepEqual(delegate.getCalls, ["second"]);

  delegate.getCalls.length = 0;
  await store.save("first", {
    version: 1,
    status: "completed",
    payload: { last_result: "incorrect" },
  });
  await globalProgress.whenIdle();
  assert.deepEqual(markers(document).map(markerState), [
    "completed",
    "completed",
  ]);
  assert.deepEqual(delegate.getCalls, ["first"]);

  delegate.getCalls.length = 0;
  await store.reset(["first"]);
  await globalProgress.whenIdle();
  assert.deepEqual(markers(document).map(markerState), ["partial", "partial"]);
  assert.deepEqual(delegate.getCalls, ["first"]);

  delegate.getCalls.length = 0;
  await store.reset();
  await globalProgress.whenIdle();
  assert.deepEqual(markers(document).map(markerState), [
    "none_completed",
    "none_completed",
  ]);
  assert.deepEqual(delegate.getCalls, []);
});


test("Zacznij od nowa w rendererze natychmiast cofa completed do partial", async () => {
  const { container, document } = createDocument();
  appendMarkedSection(document, container, "sekcja");
  appendSlot(document, container, "page-slot");
  appendTocLink(document, container, "#sekcja");
  appendTocLink(document, container, "./#sekcja");
  const definition = {
    activity_id: "first",
    version: 1,
    label: "Pytanie",
    prompt: "Wybierz odpowiedź.",
    options: [
      { option_id: "a", label: "Pierwsza" },
      { option_id: "b", label: "Druga" },
    ],
    correct_option_id: "b",
    feedback: {
      correct: "Druga odpowiedź spełnia kryterium.",
      incorrect: "Należy ponownie porównać odpowiedzi.",
    },
  };
  const manifest = {
    activities: [
      { ...definition, slot_id: "page-slot", section_id: "sekcja" },
      activity("second", "page-slot", "sekcja"),
    ],
  };
  const delegate = new MemoryProgressStore({
    first: {
      status: "completed",
      score: 1,
      attempts: 1,
      payload: { selected_option_id: "b", last_result: "correct" },
    },
    second: { status: "completed", score: 1, attempts: 1 },
  });
  const store = new NotifyingProgressStore(delegate);
  const globalProgress = createGlobalProgressController({
    document,
    manifest,
    store,
  });
  await globalProgress.ready;
  const sectionProgress = createSectionProgressController({
    document,
    manifest,
    completionSource: globalProgress,
  });
  sectionProgress.decorateCurrentPage();
  const activityRoot = await renderSingleChoice({
    activity: definition,
    store,
    document,
  });
  const restartButton = allElements(activityRoot).find(
    (element) => element.tagName === "button"
      && element.textContent === "Zacznij od nowa",
  );

  assert.deepEqual(markers(document).map(markerState), [
    "completed",
    "completed",
  ]);
  await dispatch(restartButton, "click");
  await globalProgress.whenIdle();

  assert.deepEqual(markers(document).map(markerState), ["partial", "partial"]);
  assert.equal(await delegate.get("first"), null);
  assert.equal((await delegate.get("second")).status, "completed");
});


test("section_id null i nieoznaczone wpisy ToC nie otrzymują markera", () => {
  const { container, document } = createDocument();
  appendMarkedSection(document, container, "oznaczona");
  appendSlot(document, container, "page-slot");
  appendTocLink(document, container, "#oznaczona");
  appendTocLink(document, container, "#nieoznaczona");
  const completionSource = new CompletionSource({ page: true });
  const controller = createSectionProgressController({
    document,
    manifest: {
      activities: [activity("page", "page-slot", null)],
    },
    completionSource,
  });

  assert.equal(controller.decorateCurrentPage(), 1);
  assert.equal(markers(document).length, 1);
  assert.equal(markerState(markers(document)[0]), "none");
});
