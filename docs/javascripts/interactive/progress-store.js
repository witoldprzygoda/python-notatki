export class ProgressStore {
  constructor() {
    if (new.target === ProgressStore) {
      throw new TypeError("ProgressStore jest klasą abstrakcyjną.");
    }
  }

  async get(activityId) {
    void activityId;
    throw new Error("Metoda get() nie została zaimplementowana.");
  }

  async save(activityId, state) {
    void activityId;
    void state;
    throw new Error("Metoda save() nie została zaimplementowana.");
  }

  async getSummary() {
    throw new Error("Metoda getSummary() nie została zaimplementowana.");
  }

  async reset(activityIds = null) {
    void activityIds;
    throw new Error("Metoda reset() nie została zaimplementowana.");
  }
}
