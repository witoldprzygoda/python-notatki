import assert from "node:assert/strict";
import test from "node:test";

import { NotifyingProgressStore } from "../../docs/javascripts/interactive/notifying-progress-store.js";


function createDelegate(overrides = {}) {
  return {
    async get(activityId) {
      return { activity_id: activityId };
    },
    async save() {
      return undefined;
    },
    async getSummary() {
      return { total: 0, completed: 0 };
    },
    async reset() {
      return undefined;
    },
    ...overrides,
  };
}


test("deleguje odczyty bez emitowania zdarzeń", async () => {
  const calls = [];
  const delegate = createDelegate({
    async get(activityId) {
      calls.push(["get", activityId]);
      return { activity_id: activityId, status: "completed" };
    },
    async getSummary() {
      calls.push(["getSummary"]);
      return { total: 1, completed: 1 };
    },
  });
  const store = new NotifyingProgressStore(delegate);
  const events = [];
  store.subscribe((event) => events.push(event));

  assert.deepEqual(await store.get("activity-001"), {
    activity_id: "activity-001",
    status: "completed",
  });
  assert.deepEqual(await store.getSummary(), { total: 1, completed: 1 });
  assert.deepEqual(calls, [["get", "activity-001"], ["getSummary"]]);
  assert.deepEqual(events, []);
});


test("po udanym save emituje tylko activityId i zachowuje wynik delegata", async () => {
  const delegateResult = undefined;
  const delegate = createDelegate({
    async save(activityId, state) {
      assert.equal(activityId, "activity-001");
      assert.deepEqual(state, { version: 1, status: "completed" });
      return delegateResult;
    },
  });
  const store = new NotifyingProgressStore(delegate);
  const events = [];
  store.subscribe((event) => events.push(event));

  const result = await store.save("activity-001", {
    version: 1,
    status: "completed",
  });

  assert.equal(result, delegateResult);
  assert.deepEqual(events, [{ type: "save", activityId: "activity-001" }]);
  assert.deepEqual(Object.keys(events[0]).sort(), ["activityId", "type"]);
});


test("reset rozróżnia pełny i częściowy zakres oraz zachowuje sygnaturę", async () => {
  const delegatedScopes = [];
  const delegate = createDelegate({
    async reset(activityIds = null) {
      delegatedScopes.push(activityIds);
      return activityIds === null ? "all" : "partial";
    },
  });
  const store = new NotifyingProgressStore(delegate);
  const events = [];
  store.subscribe((event) => events.push(event));

  assert.equal(await store.reset(), "all");
  const partialIds = ["activity-001", "activity-002"];
  assert.equal(await store.reset(partialIds), "partial");

  assert.deepEqual(delegatedScopes, [null, partialIds]);
  assert.deepEqual(events, [
    { type: "reset", activityIds: null },
    {
      type: "reset",
      activityIds: ["activity-001", "activity-002"],
    },
  ]);
});


test("częściowy reset używa stabilnego snapshotu zakresu", async () => {
  let releaseReset;
  let delegatedActivityIds;
  const delegate = createDelegate({
    async reset(activityIds) {
      await new Promise((resolve) => {
        releaseReset = resolve;
      });
      delegatedActivityIds = [...activityIds];
    },
  });
  const store = new NotifyingProgressStore(delegate);
  const events = [];
  store.subscribe((event) => events.push(event));
  const activityIds = ["activity-001"];

  const pendingReset = store.reset(activityIds);
  activityIds.push("activity-002");
  releaseReset();
  await pendingReset;

  assert.deepEqual(delegatedActivityIds, ["activity-001"]);
  assert.deepEqual(events, [{
    type: "reset",
    activityIds: ["activity-001"],
  }]);
});


test("nie emituje zdarzenia po odrzuconym save ani reset", async () => {
  const saveError = new Error("save failed");
  const resetError = new Error("reset failed");
  const delegate = createDelegate({
    async save() {
      throw saveError;
    },
    async reset() {
      throw resetError;
    },
  });
  const store = new NotifyingProgressStore(delegate);
  const events = [];
  store.subscribe((event) => events.push(event));

  await assert.rejects(store.save("activity-001", {}), saveError);
  await assert.rejects(store.reset(), resetError);
  assert.deepEqual(events, []);
});


test("błąd listenera nie zatrzymuje innych listenerów ani operacji store", async (t) => {
  const delegateResult = { persisted: true };
  const store = new NotifyingProgressStore(createDelegate({
    async save() {
      return delegateResult;
    },
  }));
  const listenerError = new Error("listener failed");
  const reportedErrors = [];
  t.mock.method(console, "error", (...args) => reportedErrors.push(args));
  const events = [];
  store.subscribe(() => {
    throw listenerError;
  });
  store.subscribe((event) => events.push(event));

  assert.equal(await store.save("activity-001", {}), delegateResult);
  assert.deepEqual(events, [{ type: "save", activityId: "activity-001" }]);
  assert.equal(reportedErrors.length, 1);
  assert.equal(reportedErrors[0][1], listenerError);
});


test("unsubscribe jest idempotentne", async () => {
  const store = new NotifyingProgressStore(createDelegate());
  const events = [];
  const unsubscribe = store.subscribe((event) => events.push(event));

  await store.save("activity-001", {});
  unsubscribe();
  unsubscribe();
  await store.save("activity-002", {});

  assert.deepEqual(events, [{ type: "save", activityId: "activity-001" }]);
});


test("wymaga pełnego kontraktu delegata i listenera będącego funkcją", () => {
  assert.throws(
    () => new NotifyingProgressStore({}),
    /obiektu zgodnego z ProgressStore/,
  );

  const store = new NotifyingProgressStore(createDelegate());
  assert.throws(
    () => store.subscribe(null),
    /Listener zmian postępu musi być funkcją/,
  );
});
