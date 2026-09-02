export class FakeTextNode {
  constructor(text, ownerDocument = null) {
    this.nodeType = 3;
    this.ownerDocument = ownerDocument;
    this.parentNode = null;
    this.data = String(text);
  }

  get textContent() {
    return this.data;
  }

  set textContent(value) {
    this.data = String(value);
  }
}


export class FakeElement {
  constructor(tagName, ownerDocument = null) {
    this.nodeType = 1;
    this.tagName = String(tagName).toLowerCase();
    this.ownerDocument = ownerDocument;
    this.parentNode = null;
    this.attributes = new Map();
    this.childNodes = [];
    this.className = "";
    this.dataset = {};
    this.disabled = false;
    this.hidden = false;
    this.checked = false;
    this.required = false;
    this.id = "";
    this.listeners = new Map();
    this.selectionEnd = 0;
    this.selectionStart = 0;
    this.value = "";
  }

  get children() {
    return this.childNodes.filter((child) => child instanceof FakeElement);
  }

  get textContent() {
    return this.childNodes.map((child) => child.textContent).join("");
  }

  set textContent(value) {
    this.replaceChildren();
    const text = String(value);
    if (text !== "") {
      this.append(new FakeTextNode(text, this.ownerDocument));
    }
  }

  addEventListener(type, listener) {
    const listeners = this.listeners.get(type) ?? [];
    listeners.push(listener);
    this.listeners.set(type, listeners);
  }

  append(...nodes) {
    for (const node of nodes) {
      const child = node instanceof FakeElement || node instanceof FakeTextNode
        ? node
        : new FakeTextNode(node, this.ownerDocument);
      child.parentNode = this;
      this.childNodes.push(child);
    }
  }

  appendChild(node) {
    this.append(node);
    return node;
  }

  getAttribute(name) {
    if (name === "id") {
      return this.id || null;
    }
    if (name === "class") {
      return this.className || null;
    }
    return this.attributes.get(name) ?? null;
  }

  hasAttribute(name) {
    return this.getAttribute(name) !== null;
  }

  removeAttribute(name) {
    this.attributes.delete(name);
    if (name === "id") {
      this.id = "";
    } else if (name === "class") {
      this.className = "";
    }
  }

  replaceChildren(...nodes) {
    for (const child of this.childNodes) {
      child.parentNode = null;
    }
    this.childNodes = [];
    this.append(...nodes);
  }

  setAttribute(name, value) {
    const stringValue = String(value);
    if (name === "id") {
      this.id = stringValue;
    } else if (name === "class") {
      this.className = stringValue;
    } else {
      this.attributes.set(name, stringValue);
    }
  }

  setSelectionRange(start, end) {
    this.selectionStart = start;
    this.selectionEnd = end;
  }
}


export function createFakeDocument() {
  const document = {
    createElement(tagName) {
      return new FakeElement(tagName, document);
    },
    createTextNode(text) {
      return new FakeTextNode(text, document);
    },
  };
  return document;
}


export function allElements(root) {
  return [root, ...root.children.flatMap(allElements)];
}


export function findElement(root, predicate) {
  return allElements(root).find(predicate);
}


export function findElements(root, predicate) {
  return allElements(root).filter(predicate);
}


export function hasClass(element, className) {
  return element.className.split(/\s+/).includes(className);
}


export function findByClass(root, className) {
  return findElement(root, (element) => hasClass(element, className));
}


export async function dispatch(element, type, event = {}) {
  for (const listener of element.listeners.get(type) ?? []) {
    await listener(event);
  }
}
