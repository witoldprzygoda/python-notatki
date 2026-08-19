import assert from "node:assert/strict";
import test from "node:test";

import {
  createSingleChoiceProgressState,
} from "../../docs/javascripts/interactive/activities/single-choice.js";


const activity = {
  activity_id: "flow-for-quiz-001",
  version: 1,
  correct_option_id: "b",
};


test("niepoprawna pierwsza próba rozpoczyna aktywność", () => {
  assert.deepEqual(
    createSingleChoiceProgressState(activity, null, "a"),
    {
      version: 1,
      status: "in_progress",
      score: 0,
      attempts: 1,
      payload: {
        selected_option_id: "a",
        last_result: "incorrect",
      },
    },
  );
});


test("poprawna próba kończy aktywność", () => {
  const previousState = {
    status: "in_progress",
    score: 0,
    attempts: 1,
  };

  assert.deepEqual(
    createSingleChoiceProgressState(activity, previousState, "b"),
    {
      version: 1,
      status: "completed",
      score: 1,
      attempts: 2,
      payload: {
        selected_option_id: "b",
        last_result: "correct",
      },
    },
  );
});


test("późniejsza błędna próba nie cofa ukończenia ani wyniku", () => {
  const previousState = {
    status: "completed",
    score: 1,
    attempts: 2,
    payload: {
      selected_option_id: "b",
      last_result: "correct",
    },
  };

  assert.deepEqual(
    createSingleChoiceProgressState(activity, previousState, "c"),
    {
      version: 1,
      status: "completed",
      score: 1,
      attempts: 3,
      payload: {
        selected_option_id: "c",
        last_result: "incorrect",
      },
    },
  );
});
