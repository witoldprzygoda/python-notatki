import assert from "node:assert/strict";
import test from "node:test";


class MemoryStorage {
  constructor() {
    this.items = new Map();
  }

  getItem(key) {
    return this.items.has(String(key)) ? this.items.get(String(key)) : null;
  }

  removeItem(key) {
    this.items.delete(String(key));
  }

  setItem(key, value) {
    this.items.set(String(key), String(value));
  }
}


class FakeElement {
  constructor(tagName, ownerDocument) {
    this.tagName = String(tagName).toLowerCase();
    this.ownerDocument = ownerDocument;
    this.parentNode = null;
    this.childNodes = [];
    this.attributes = new Map();
    this.className = "";
    this.id = "";
    this._textContent = "";
  }

  get children() {
    return this.childNodes;
  }

  get textContent() {
    return this._textContent
      + this.childNodes.map((child) => child.textContent).join("");
  }

  set textContent(value) {
    this.replaceChildren();
    this._textContent = String(value);
  }

  append(...nodes) {
    for (const node of nodes) {
      this.#detach(node);
      node.parentNode = this;
      this.childNodes.push(node);
    }
  }

  before(node) {
    if (this.parentNode) {
      this.parentNode.insertBefore(node, this);
    }
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
    this.#detach(node);
    const index = this.childNodes.indexOf(referenceNode);
    if (index === -1) {
      this.append(node);
      return node;
    }
    node.parentNode = this;
    this.childNodes.splice(index, 0, node);
    return node;
  }

  prepend(node) {
    this.#detach(node);
    node.parentNode = this;
    this.childNodes.unshift(node);
  }

  querySelector(selector) {
    return this.querySelectorAll(selector)[0] ?? null;
  }

  querySelectorAll(selector) {
    return this.#descendants().filter((element) => element.#matches(selector));
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

  #descendants() {
    return this.childNodes.flatMap((child) => [child, ...child.#descendants()]);
  }

  #detach(node) {
    node.parentNode?.removeChild(node);
  }

  #matches(selector) {
    if (/^\.[a-z0-9_-]+$/i.test(selector)) {
      return this.className.split(/\s+/).includes(selector.slice(1));
    }
    if (/^[a-z][a-z0-9-]*$/i.test(selector)) {
      return this.tagName === selector.toLowerCase();
    }
    const attribute = selector.match(/^\[([^=\]]+)(?:="([^"]*)")?\]$/);
    if (!attribute) {
      return false;
    }
    const [, name, expectedValue] = attribute;
    if (!this.attributes.has(name)) {
      return false;
    }
    return expectedValue === undefined
      || this.attributes.get(name) === expectedValue;
  }
}


function createDocumentWithoutActivitySlot() {
  const document = {
    baseURI: "https://example.test/course/page/",
    createElement(tagName) {
      return new FakeElement(tagName, document);
    },
    querySelector(selector) {
      if (selector === ".md-sidebar--primary .md-sidebar__scrollwrap") {
        return document.body.querySelectorAll(".md-sidebar__scrollwrap").find(
          (element) => element.parentNode?.className
            .split(/\s+/)
            .includes("md-sidebar--primary"),
        ) ?? null;
      }
      return document.body.querySelector(selector);
    },
    querySelectorAll(selector) {
      return document.body.querySelectorAll(selector);
    },
  };
  document.body = document.createElement("body");
  const header = document.createElement("header");
  header.setAttribute("data-md-component", "header");
  const container = document.createElement("div");
  container.setAttribute("data-md-component", "container");
  document.body.append(header, container);
  return document;
}


function appendPrimarySidebar(document, container) {
  const sidebar = document.createElement("div");
  sidebar.className = "md-sidebar md-sidebar--primary";
  sidebar.setAttribute("data-md-type", "navigation");

  const scrollwrap = document.createElement("div");
  scrollwrap.className = "md-sidebar__scrollwrap";
  const inner = document.createElement("div");
  inner.className = "md-sidebar__inner";
  const navigation = document.createElement("nav");
  navigation.className = "md-nav md-nav--primary";

  inner.append(navigation);
  scrollwrap.append(inner);
  sidebar.append(scrollwrap);
  container.append(sidebar);
}


function installSlotlessTocPage(document, sectionId) {
  const container = document.querySelector("[data-md-component=\"container\"]");
  container.replaceChildren();
  appendPrimarySidebar(document, container);

  const heading = document.createElement("h2");
  heading.setAttribute("id", sectionId);
  heading.setAttribute("data-activity-section", "true");
  container.append(heading);

  for (const href of [`#${sectionId}`, `./#${sectionId}`]) {
    const toc = document.createElement("ul");
    toc.setAttribute("data-md-component", "toc");
    const link = document.createElement("a");
    link.setAttribute("href", href);
    link.textContent = "Sekcja";
    toc.append(link);
    container.append(toc);
  }
}


function createDocumentStream() {
  let callback;
  return {
    emit() {
      return callback();
    },
    subscribe(next) {
      callback = next;
    },
  };
}


function installGlobals({
  document,
  documentStream,
  fetchImplementation,
  storage = new MemoryStorage(),
}) {
  let workerCreated = false;
  globalThis.window = { localStorage: storage };
  globalThis.document = document;
  globalThis.document$ = documentStream;
  globalThis.fetch = fetchImplementation;
  globalThis.Worker = class {
    constructor() {
      workerCreated = true;
      throw new Error("Worker nie powinien powstać podczas inicjalizacji.");
    }
  };
  return () => workerCreated;
}


function removeGlobals() {
  delete globalThis.Worker;
  delete globalThis.document$;
  delete globalThis.document;
  delete globalThis.fetch;
  delete globalThis.window;
}


function assertNoGlobalProgressUi(document) {
  assert.equal(
    document.querySelector("[data-interactive-global-progress]"),
    null,
  );
  assert.equal(document.querySelectorAll("progress").length, 0);
  assert.equal(document.body.textContent.includes("Postęp ćwiczeń"), false);
}


const manifest = {
  schema_version: 2,
  activities: [
    {
      activity_id: "flow-for-quiz-001",
      page_url: "other-page/",
      slot_id: "other-page-slot",
      section_id: "other-section",
      type: "single_choice",
    },
    {
      activity_id: "flow-for-code-001",
      page_url: "other-page/",
      slot_id: "other-page-slot",
      section_id: "other-section",
      type: "code",
    },
  ],
};


test("szybkie emisje używają jednego manifestu bez globalnego UI", async () => {
  const document = createDocumentWithoutActivitySlot();
  installSlotlessTocPage(document, "first-section");
  const documentStream = createDocumentStream();
  let resolveFetch;
  let fetchCount = 0;
  const fetchPromise = new Promise((resolve) => {
    resolveFetch = resolve;
  });
  const workerWasCreated = installGlobals({
    document,
    documentStream,
    fetchImplementation() {
      fetchCount += 1;
      return fetchPromise;
    },
  });

  try {
    await import("../../docs/javascripts/interactive/bootstrap.js?lifecycle-cache");
    const firstNavigation = documentStream.emit();
    const secondNavigation = documentStream.emit();

    assert.equal(fetchCount, 1);
    resolveFetch({
      ok: true,
      async json() {
        return manifest;
      },
    });
    await Promise.all([firstNavigation, secondNavigation]);

    assert.equal(fetchCount, 1);
    assertNoGlobalProgressUi(document);
    assert.equal(document.querySelector("[data-activity-slot]"), null);
    assert.equal(
      document.querySelectorAll("[data-interactive-section-progress]").length,
      2,
    );

    await documentStream.emit();
    assert.equal(fetchCount, 1);
    assertNoGlobalProgressUi(document);
    assert.equal(
      document.querySelectorAll("[data-interactive-section-progress]").length,
      2,
    );

    installSlotlessTocPage(document, "second-section");
    await documentStream.emit();
    assert.equal(fetchCount, 1);
    assertNoGlobalProgressUi(document);
    assert.equal(
      document.querySelectorAll("[data-interactive-section-progress]").length,
      2,
    );
    assert.equal(workerWasCreated(), false);
  } finally {
    removeGlobals();
  }
});


test("nieudane pobranie manifestu jest ponawiane przy następnej emisji", async () => {
  const document = createDocumentWithoutActivitySlot();
  installSlotlessTocPage(document, "retry-section");
  const documentStream = createDocumentStream();
  let fetchCount = 0;
  const originalWarn = console.warn;
  console.warn = () => {};
  const workerWasCreated = installGlobals({
    document,
    documentStream,
    fetchImplementation() {
      fetchCount += 1;
      if (fetchCount === 1) {
        return Promise.resolve({ ok: false, status: 503 });
      }
      return Promise.resolve({
        ok: true,
        async json() {
          return manifest;
        },
      });
    },
  });

  try {
    await import("../../docs/javascripts/interactive/bootstrap.js?lifecycle-retry");
    await documentStream.emit();
    assert.equal(fetchCount, 1);
    assert.equal(
      document.querySelector("[data-interactive-global-progress]"),
      null,
    );
    assert.equal(
      document.querySelectorAll("[data-interactive-section-progress]").length,
      0,
    );

    await documentStream.emit();
    assert.equal(fetchCount, 2);
    assertNoGlobalProgressUi(document);
    assert.equal(
      document.querySelectorAll("[data-interactive-section-progress]").length,
      2,
    );
    assert.equal(workerWasCreated(), false);
  } finally {
    console.warn = originalWarn;
    removeGlobals();
  }
});


test("błąd hydratacji postępu nie tworzy fałszywych markerów sekcji", async () => {
  const document = createDocumentWithoutActivitySlot();
  installSlotlessTocPage(document, "unavailable-section");
  const documentStream = createDocumentStream();
  const originalError = console.error;
  const originalWarn = console.warn;
  console.error = () => {};
  console.warn = () => {};
  const workerWasCreated = installGlobals({
    document,
    documentStream,
    fetchImplementation() {
      return Promise.resolve({
        ok: true,
        async json() {
          return manifest;
        },
      });
    },
    storage: {
      getItem() {
        throw new Error("Magazyn jest niedostępny.");
      },
      removeItem() {},
      setItem() {},
    },
  });

  try {
    await import("../../docs/javascripts/interactive/bootstrap.js?hydration-failure");
    await documentStream.emit();

    assert.equal(
      document.querySelectorAll("[data-interactive-section-progress]").length,
      0,
    );
    assertNoGlobalProgressUi(document);
    assert.equal(workerWasCreated(), false);
  } finally {
    console.error = originalError;
    console.warn = originalWarn;
    removeGlobals();
  }
});
