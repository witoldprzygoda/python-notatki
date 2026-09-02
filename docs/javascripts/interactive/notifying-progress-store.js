import { ProgressStore } from "./progress-store.js";


function requireDelegate(delegate) {
  const methods = ["get", "save", "getSummary", "reset"];
  if (
    delegate === null
    || typeof delegate !== "object"
    || methods.some((method) => typeof delegate[method] !== "function")
  ) {
    throw new TypeError("NotifyingProgressStore wymaga obiektu zgodnego z ProgressStore.");
  }
}


function requireListener(listener) {
  if (typeof listener !== "function") {
    throw new TypeError("Listener zmian postępu musi być funkcją.");
  }
}


export class NotifyingProgressStore extends ProgressStore {
  constructor(delegate) {
    super();
    requireDelegate(delegate);
    this.delegate = delegate;
    this.listeners = new Set();
  }

  subscribe(listener) {
    requireListener(listener);
    this.listeners.add(listener);

    let subscribed = true;
    return () => {
      if (!subscribed) {
        return;
      }
      subscribed = false;
      this.listeners.delete(listener);
    };
  }

  async get(activityId) {
    return this.delegate.get(activityId);
  }

  async save(activityId, state) {
    const result = await this.delegate.save(activityId, state);
    this.#notify(Object.freeze({ type: "save", activityId }));
    return result;
  }

  async getSummary() {
    return this.delegate.getSummary();
  }

  async reset(activityIds = null) {
    const eventActivityIds = Array.isArray(activityIds)
      ? Object.freeze([...activityIds])
      : activityIds;
    const delegatedActivityIds = Array.isArray(eventActivityIds)
      ? [...eventActivityIds]
      : eventActivityIds;
    const result = await this.delegate.reset(delegatedActivityIds);
    this.#notify(Object.freeze({
      type: "reset",
      activityIds: eventActivityIds,
    }));
    return result;
  }

  #notify(event) {
    for (const listener of [...this.listeners]) {
      try {
        listener(event);
      } catch (error) {
        console.error("Błąd listenera zmian postępu.", error);
      }
    }
  }
}
