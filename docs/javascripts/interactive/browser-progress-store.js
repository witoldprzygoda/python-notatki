import { ProgressStore } from "./progress-store.js";


export const DEFAULT_PROGRESS_STORAGE_KEY = "python-notatki.progress.v1";

const SCHEMA_VERSION = 1;


function getDefaultStorage() {
  if (typeof window === "undefined") {
    return undefined;
  }
  return window.localStorage;
}


function createEmptyDocument() {
  return {
    schema_version: SCHEMA_VERSION,
    activities: {},
  };
}


function isRecord(value) {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}


function requireActivityId(activityId) {
  if (typeof activityId !== "string" || activityId.trim() === "") {
    throw new TypeError("activityId musi być niepustym tekstem.");
  }
}


function requireState(state) {
  if (!isRecord(state)) {
    throw new TypeError("Stan aktywności musi być obiektem.");
  }
  if (
    !Number.isInteger(state.version)
    || state.version < 1
    || typeof state.status !== "string"
    || state.status.trim() === ""
  ) {
    throw new TypeError("Stan wymaga poprawnych pól version i status.");
  }
}


export class BrowserProgressStore extends ProgressStore {
  constructor(
    storage = getDefaultStorage(),
    storageKey = DEFAULT_PROGRESS_STORAGE_KEY,
  ) {
    super();
    if (
      !storage
      || typeof storage.getItem !== "function"
      || typeof storage.setItem !== "function"
      || typeof storage.removeItem !== "function"
    ) {
      throw new TypeError("BrowserProgressStore wymaga obiektu zgodnego z Web Storage.");
    }
    this.storage = storage;
    this.storageKey = storageKey;
  }

  async get(activityId) {
    requireActivityId(activityId);
    const document = this.#readDocument();
    const state = document.activities[activityId];
    return isRecord(state) ? { ...state } : null;
  }

  async save(activityId, state) {
    requireActivityId(activityId);
    requireState(state);

    const document = this.#readDocument();
    const savedState = {
      activity_id: activityId,
      version: state.version,
      status: state.status,
      updated_at: new Date().toISOString(),
    };
    document.activities[activityId] = savedState;
    this.storage.setItem(this.storageKey, JSON.stringify(document));
    return { ...savedState };
  }

  async getSummary() {
    const document = this.#readDocument();
    const states = Object.values(document.activities).filter(isRecord);
    return {
      total: states.length,
      completed: states.filter((state) => state.status === "completed").length,
    };
  }

  async reset() {
    this.storage.removeItem(this.storageKey);
  }

  #readDocument() {
    const rawDocument = this.storage.getItem(this.storageKey);
    if (rawDocument === null) {
      return createEmptyDocument();
    }

    try {
      const document = JSON.parse(rawDocument);
      if (
        !isRecord(document)
        || document.schema_version !== SCHEMA_VERSION
        || !isRecord(document.activities)
      ) {
        return createEmptyDocument();
      }
      return document;
    } catch (error) {
      if (!(error instanceof SyntaxError)) {
        throw error;
      }
      return createEmptyDocument();
    }
  }
}
