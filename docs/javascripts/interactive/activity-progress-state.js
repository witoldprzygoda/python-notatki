const COMPLETION_METHODS = new Set([
  "checked",
  "solution_shown",
  "self_marked",
]);

const MANUAL_COMPLETION_METHODS = new Set([
  "solution_shown",
  "self_marked",
]);


function isRecord(value) {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}


function previousAttempts(state) {
  return Number.isInteger(state?.attempts) && state.attempts >= 0
    ? state.attempts
    : 0;
}


function hasOwnScore(state) {
  return isRecord(state)
    && Object.prototype.hasOwnProperty.call(state, "score");
}


function storedCompletionMethod(state) {
  const method = state?.payload?.completion_method;
  return COMPLETION_METHODS.has(method) ? method : null;
}


function applyCompletionMethod(
  payload,
  previousState,
  completed,
  transitionMethod,
) {
  const previousMethod = getCompletionMethod(previousState);
  if (isCompleted(previousState)) {
    if (previousMethod !== null) {
      payload.completion_method = previousMethod;
    } else {
      delete payload.completion_method;
    }
  } else if (completed) {
    payload.completion_method = transitionMethod;
  } else {
    delete payload.completion_method;
  }
  return payload;
}


function withOptionalScore(state, previousState) {
  if (hasOwnScore(previousState)) {
    state.score = previousState.score;
  }
  return state;
}


export function isCompleted(state) {
  return state?.status === "completed";
}


export function getCompletionMethod(state) {
  if (!isCompleted(state)) {
    return null;
  }
  const storedMethod = storedCompletionMethod(state);
  if (storedMethod !== null) {
    return storedMethod;
  }
  return isCompleted(state) && state?.score === 1 ? "checked" : null;
}


export function mergeProgressPayload(
  previousState,
  patch = {},
  removeKeys = [],
) {
  const payload = isRecord(previousState?.payload)
    ? { ...previousState.payload }
    : {};
  Object.assign(payload, patch);
  for (const key of removeKeys) {
    delete payload[key];
  }
  return payload;
}


export function createCheckedProgressState(
  activity,
  previousState,
  {
    isCorrect,
    payloadPatch = {},
    removePayloadKeys = [],
  },
) {
  const completed = isCompleted(previousState) || isCorrect;
  const payload = mergeProgressPayload(
    previousState,
    payloadPatch,
    removePayloadKeys,
  );
  applyCompletionMethod(payload, previousState, completed, "checked");

  return {
    version: activity.version,
    status: completed ? "completed" : "in_progress",
    score: previousState?.score === 1 || isCorrect ? 1 : 0,
    attempts: previousAttempts(previousState) + 1,
    payload,
  };
}


export function createManualCompletionProgressState(
  activity,
  previousState,
  {
    completionMethod: requestedMethod,
    payloadPatch = {},
    removePayloadKeys = [],
  },
) {
  if (!MANUAL_COMPLETION_METHODS.has(requestedMethod)) {
    throw new TypeError(
      "Ręczna metoda ukończenia musi mieć wartość solution_shown albo self_marked.",
    );
  }

  const payload = mergeProgressPayload(
    previousState,
    payloadPatch,
    removePayloadKeys,
  );
  applyCompletionMethod(payload, previousState, true, requestedMethod);

  return withOptionalScore({
    version: activity.version,
    status: "completed",
    attempts: previousAttempts(previousState),
    payload,
  }, previousState);
}


export function createCodeRunProgressState(
  activity,
  previousState,
  sourceCode,
) {
  const completed = isCompleted(previousState);
  const payload = mergeProgressPayload(
    previousState,
    { source_code: sourceCode },
    ["last_result"],
  );
  applyCompletionMethod(payload, previousState, completed, null);

  return withOptionalScore({
    version: activity.version,
    status: completed ? "completed" : "in_progress",
    attempts: previousAttempts(previousState),
    payload,
  }, previousState);
}
