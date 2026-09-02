function collectActivityIds(manifest) {
  const activities = Array.isArray(manifest?.activities)
    ? manifest.activities
    : [];
  const activityIds = new Set();

  for (const activity of activities) {
    if (
      typeof activity?.activity_id === "string"
      && activity.activity_id.trim() !== ""
    ) {
      activityIds.add(activity.activity_id);
    }
  }

  return [...activityIds];
}


function requireDependencies({ store }) {
  if (
    !store
    || typeof store.get !== "function"
    || typeof store.subscribe !== "function"
  ) {
    throw new TypeError("Model postępu wymaga obserwowalnego ProgressStore.");
  }
}


/**
 * Tworzy bezgłowy model ukończeń dla activity_id z bieżącego manifestu.
 * Store pozostaje jedynym źródłem prawdy; eventy zawierają tylko zakres zmiany.
 */
export function createGlobalProgressController({ manifest, store }) {
  requireDependencies({ store });

  const activityIds = collectActivityIds(manifest);
  const trackedActivityIds = new Set(activityIds);
  const completedByActivityId = new Map(
    activityIds.map((activityId) => [activityId, false]),
  );
  let destroyed = false;
  let hydrationState = "pending";
  let operationQueue = Promise.resolve();
  const activityCompletionListeners = new Set();

  function getSnapshot() {
    return {
      completed: [...completedByActivityId.values()].filter(Boolean).length,
      total: activityIds.length,
    };
  }

  function getActivityCompletion(activityId) {
    if (
      destroyed
      || hydrationState !== "ready"
      || !trackedActivityIds.has(activityId)
    ) {
      return undefined;
    }
    return completedByActivityId.get(activityId);
  }

  function subscribeActivityCompletion(listener) {
    if (typeof listener !== "function") {
      throw new TypeError("Listener ukończenia aktywności musi być funkcją.");
    }
    if (destroyed) {
      return () => {};
    }

    activityCompletionListeners.add(listener);
    let subscribed = true;
    return () => {
      if (!subscribed) {
        return;
      }
      subscribed = false;
      activityCompletionListeners.delete(listener);
    };
  }

  function notifyActivityCompletion(ids) {
    if (destroyed) {
      return;
    }
    const changedActivityIds = Object.freeze(
      [...new Set(ids)].filter((activityId) => (
        trackedActivityIds.has(activityId)
      )),
    );
    if (changedActivityIds.length === 0) {
      return;
    }

    const event = Object.freeze({ activityIds: changedActivityIds });
    for (const listener of [...activityCompletionListeners]) {
      try {
        listener(event);
      } catch (error) {
        console.error("Błąd listenera ukończenia aktywności.", error);
      }
    }
  }

  function applyState(activityId, state) {
    completedByActivityId.set(
      activityId,
      state?.status === "completed",
    );
  }

  async function refreshActivityIds(ids) {
    const uniqueTrackedIds = [...new Set(ids)].filter(
      (activityId) => trackedActivityIds.has(activityId),
    );
    if (uniqueTrackedIds.length === 0) {
      return [];
    }

    const states = await Promise.all(
      uniqueTrackedIds.map((activityId) => store.get(activityId)),
    );
    if (destroyed) {
      return [];
    }
    uniqueTrackedIds.forEach((activityId, index) => {
      applyState(activityId, states[index]);
    });
    return uniqueTrackedIds;
  }

  async function handleEvent(event) {
    if (destroyed || !event || typeof event !== "object") {
      return;
    }
    if (event.type === "save") {
      const changedActivityIds = await refreshActivityIds([event.activityId]);
      notifyActivityCompletion(changedActivityIds);
      return;
    }
    if (event.type !== "reset") {
      return;
    }
    if (event.activityIds === null) {
      for (const activityId of activityIds) {
        completedByActivityId.set(activityId, false);
      }
      notifyActivityCompletion(activityIds);
      return;
    }
    if (Array.isArray(event.activityIds)) {
      const changedActivityIds = await refreshActivityIds(event.activityIds);
      notifyActivityCompletion(changedActivityIds);
    }
  }

  function enqueue(operation) {
    const result = operationQueue.then(operation);
    operationQueue = result.catch((error) => {
      console.error("Nie udało się zaktualizować modelu postępu.", error);
    });
    return result;
  }

  const unsubscribe = store.subscribe((event) => {
    void enqueue(() => handleEvent(event));
  });
  const ready = enqueue(async () => {
    try {
      await refreshActivityIds(activityIds);
      hydrationState = "ready";
      return getSnapshot();
    } catch (error) {
      hydrationState = "failed";
      throw error;
    }
  });

  function destroy() {
    if (destroyed) {
      return;
    }
    destroyed = true;
    unsubscribe();
    activityCompletionListeners.clear();
  }

  return {
    ready,
    destroy,
    getActivityCompletion,
    getSnapshot,
    subscribeActivityCompletion,
    whenIdle() {
      return operationQueue;
    },
  };
}
