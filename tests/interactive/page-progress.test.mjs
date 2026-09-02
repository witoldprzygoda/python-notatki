import assert from "node:assert/strict";
import test from "node:test";

import {
  createPageProgressController,
  pageUrlKey,
} from "../../docs/javascripts/interactive/page-progress.js";


class FakeElement {
  constructor(tagName, ownerDocument) {
    this.tagName = String(tagName).toLowerCase();
    this.ownerDocument = ownerDocument;
    this.parentNode = null;
    this.childNodes = [];
    this.attributes = new Map();
    this.className = "";
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

  append(...nodes) {
    for (const node of nodes) {
      node.parentNode?.removeChild(node);
      node.parentNode = this;
      this.childNodes.push(node);
    }
  }

  getAttribute(name) {
    if (name === "class") {
      return this.className || null;
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
    baseURI: "https://example.test/course/current/",
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
  return document;
}


function appendSidebar(document) {
  const sidebar = document.createElement("div");
  sidebar.className = "md-sidebar md-sidebar--primary";
  sidebar.setAttribute("data-md-type", "navigation");
  const navigation = document.createElement("nav");
  navigation.className = "md-nav md-nav--primary";
  sidebar.append(navigation);
  document.body.append(sidebar);
  return navigation;
}


function appendLink(document, parent, href, labelText = "Strona") {
  const link = document.createElement("a");
  link.className = "md-nav__link";
  link.setAttribute("href", href);
  const label = document.createElement("span");
  label.className = "md-ellipsis";
  label.textContent = labelText;
  link.append(label);
  parent.append(link);
  return link;
}


function appendGroupLabel(document, parent) {
  const label = document.createElement("label");
  label.className = "md-nav__link";
  const text = document.createElement("span");
  text.className = "md-ellipsis";
  text.textContent = "Grupa";
  label.append(text);
  parent.append(label);
  return label;
}


function appendLocalTocLink(document, parent, href) {
  const toc = document.createElement("nav");
  toc.className = "md-nav md-nav--secondary";
  const list = document.createElement("ul");
  list.setAttribute("data-md-component", "toc");
  toc.append(list);
  parent.append(toc);
  return appendLink(document, list, href, "Sekcja");
}


function pageMarkers(element) {
  return element.querySelectorAll("[data-interactive-page-progress]");
}


class CompletionSource {
  constructor(states = {}) {
    this.states = new Map(Object.entries(states));
    this.listeners = new Set();
    this.available = true;
    this.getCalls = [];
  }

  getActivityCompletion(activityId) {
    this.getCalls.push(activityId);
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


function activity(activityId, pageUrl) {
  return { activity_id: activityId, page_url: pageUrl };
}


test("porównuje wygenerowane page_url po URL bez query i fragmentu", () => {
  const siteBaseUrl = "https://example.test/course/";

  assert.equal(
    pageUrlKey("04-sterowanie/petle/", siteBaseUrl),
    pageUrlKey(
      "https://example.test/course/04-sterowanie/petle/?view=all#sekcja",
      siteBaseUrl,
    ),
  );
  assert.equal(
    pageUrlKey("", siteBaseUrl),
    "https://example.test/course/",
  );
  assert.notEqual(
    pageUrlKey("lekcja/", siteBaseUrl),
    pageUrlKey("lekcja.html", siteBaseUrl),
  );
  assert.equal(pageUrlKey("http://[", siteBaseUrl), null);
});


test("cztery ukończone aktywności dają completed dla obu stron", () => {
  const document = createDocument();
  const navigation = appendSidebar(document);
  const conditions = appendLink(
    document,
    navigation,
    "../04-sterowanie/wyrazenia-warunkowe/",
    "Wyrażenia warunkowe",
  );
  const loops = appendLink(
    document,
    navigation,
    "../04-sterowanie/petle-i-iteratory/",
    "Pętle i iteratory",
  );
  const source = new CompletionSource({
    "flow-for-quiz-001": true,
    "flow-for-code-001": true,
    "flow-if-quiz-001": true,
    "flow-match-code-001": true,
  });
  const controller = createPageProgressController({
    document,
    manifest: {
      activities: [
        activity(
          "flow-for-quiz-001",
          "04-sterowanie/petle-i-iteratory/",
        ),
        activity(
          "flow-for-code-001",
          "04-sterowanie/petle-i-iteratory/",
        ),
        activity(
          "flow-if-quiz-001",
          "04-sterowanie/wyrazenia-warunkowe/",
        ),
        activity(
          "flow-match-code-001",
          "04-sterowanie/wyrazenia-warunkowe/",
        ),
      ],
    },
    completionSource: source,
    siteBaseUrl: "https://example.test/course/",
  });

  assert.equal(controller.decorateNavigation(), 2);
  assert.equal(
    pageMarkers(conditions)[0].getAttribute("data-state"),
    "completed",
  );
  assert.equal(
    pageMarkers(loops)[0].getAttribute("data-state"),
    "completed",
  );
});


test("brak page_url usuwa markery i ostrzega tylko raz", (t) => {
  const document = createDocument();
  const navigation = appendSidebar(document);
  const lesson = appendLink(document, navigation, "../lesson/");
  const source = new CompletionSource({ first: true, missing: true });
  const warning = t.mock.method(console, "warn", () => {});
  const controller = createPageProgressController({
    document,
    manifest: {
      activities: [
        activity("first", "lesson/"),
        { activity_id: "missing" },
      ],
    },
    completionSource: source,
    siteBaseUrl: "https://example.test/course/",
  });

  assert.equal(controller.decorateNavigation(), 0);
  assert.equal(controller.decorateNavigation(), 0);
  source.emit(["missing"]);

  assert.equal(pageMarkers(lesson).length, 0);
  assert.equal(warning.mock.callCount(), 1);
  assert.match(warning.mock.calls[0].arguments[0], /page_url/);
  assert.match(warning.mock.calls[0].arguments[0], /missing/);
});


test("dekoruje tylko rzeczywiste linki stron i nie zmienia linków Material", () => {
  const document = createDocument();
  const navigation = appendSidebar(document);
  const lesson = appendLink(document, navigation, "../lesson/?source=nav");
  lesson.className = "md-nav__link md-nav__link--active";
  lesson.setAttribute("style", "border-left: 3px solid blue");
  const plain = appendLink(document, navigation, "../plain/");
  const group = appendGroupLabel(document, navigation);
  const external = appendLink(
    document,
    navigation,
    "https://outside.test/page/",
  );
  const fragment = appendLink(document, navigation, "#section");
  const tocLink = appendLocalTocLink(document, navigation, "../lesson/");
  const source = new CompletionSource({ first: true, second: false });
  const controller = createPageProgressController({
    document,
    manifest: {
      activities: [
        activity("first", "lesson/"),
        activity("second", "lesson/"),
      ],
    },
    completionSource: source,
    siteBaseUrl: "https://example.test/course/",
  });
  const lessonHref = lesson.getAttribute("href");
  const lessonClass = lesson.className;
  const lessonStyle = lesson.getAttribute("style");

  assert.equal(controller.decorateNavigation(), 2);

  assert.equal(pageMarkers(lesson).length, 1);
  assert.equal(pageMarkers(lesson)[0].getAttribute("data-state"), "partial");
  assert.equal(lesson.children[0].className, "md-ellipsis");
  assert.equal(lesson.children[1], pageMarkers(lesson)[0]);
  assert.equal(lesson.getAttribute("href"), lessonHref);
  assert.equal(lesson.className, lessonClass);
  assert.equal(lesson.getAttribute("style"), lessonStyle);

  assert.equal(pageMarkers(plain).length, 1);
  assert.equal(pageMarkers(plain)[0].getAttribute("data-state"), "none");
  assert.equal(pageMarkers(group).length, 0);
  assert.equal(pageMarkers(external).length, 0);
  assert.equal(pageMarkers(fragment).length, 0);
  assert.equal(pageMarkers(tocLink).length, 0);
});


test("aktualizuje wszystkie kopie linku bez własnego cache'u ukończeń", () => {
  const document = createDocument();
  const firstNavigation = appendSidebar(document);
  const secondNavigation = appendSidebar(document);
  const firstLink = appendLink(document, firstNavigation, "../lesson/");
  const secondLink = appendLink(document, secondNavigation, "../lesson/");
  const source = new CompletionSource({ first: false, second: false });
  const controller = createPageProgressController({
    document,
    manifest: {
      activities: [
        activity("first", "lesson/"),
        activity("second", "lesson/"),
      ],
    },
    completionSource: source,
    siteBaseUrl: "https://example.test/course/",
  });

  assert.equal(controller.decorateNavigation(), 2);
  assert.equal(pageMarkers(firstLink)[0].getAttribute("data-state"), "none_completed");
  assert.equal(pageMarkers(secondLink)[0].getAttribute("data-state"), "none_completed");

  source.set("first", true);
  assert.equal(pageMarkers(firstLink)[0].getAttribute("data-state"), "partial");
  assert.equal(pageMarkers(secondLink)[0].getAttribute("data-state"), "partial");

  source.set("second", true);
  assert.equal(pageMarkers(firstLink)[0].getAttribute("data-state"), "completed");
  assert.equal(pageMarkers(secondLink)[0].getAttribute("data-state"), "completed");

  source.set("first", false);
  assert.equal(pageMarkers(firstLink)[0].getAttribute("data-state"), "partial");
  assert.equal(source.getCalls.includes("first"), true);
  assert.equal(source.getCalls.includes("second"), true);
});


test("wielokrotne dekorowanie nie duplikuje raili", () => {
  const document = createDocument();
  const navigation = appendSidebar(document);
  const link = appendLink(document, navigation, "../lesson/");
  const source = new CompletionSource({ first: true });
  const controller = createPageProgressController({
    document,
    manifest: { activities: [activity("first", "lesson/")] },
    completionSource: source,
    siteBaseUrl: "https://example.test/course/",
  });

  assert.equal(controller.decorateNavigation(), 1);
  assert.equal(controller.decorateNavigation(), 1);
  assert.equal(pageMarkers(link).length, 1);
  assert.equal(
    document.querySelectorAll("[data-interactive-page-progress]").length,
    1,
  );
});


test("niedostępny model nie jest przedstawiany jako szary stan", () => {
  const document = createDocument();
  const navigation = appendSidebar(document);
  const link = appendLink(document, navigation, "../lesson/");
  const source = new CompletionSource({ first: false });
  const controller = createPageProgressController({
    document,
    manifest: { activities: [activity("first", "lesson/")] },
    completionSource: source,
    siteBaseUrl: "https://example.test/course/",
  });

  source.available = false;
  assert.equal(controller.decorateNavigation(), 0);
  assert.equal(pageMarkers(link).length, 0);

  source.available = true;
  assert.equal(controller.decorateNavigation(), 1);
  assert.equal(pageMarkers(link)[0].getAttribute("data-state"), "none_completed");

  source.available = false;
  source.emit(["first"]);
  assert.equal(pageMarkers(link).length, 0);
});
