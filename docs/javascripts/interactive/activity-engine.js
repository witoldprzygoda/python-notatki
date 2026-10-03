import { createPageActivities } from "./page-activities.js";


export class ActivityEngine {
  constructor({ store, renderers }) {
    this.store = store;
    this.renderers = renderers;
    this.renderedSlots = new WeakSet();
    this.pendingSlots = new WeakSet();
  }

  async render(root, activities) {
    const slots = Array.from(root.querySelectorAll("[data-activity-slot]"));
    await Promise.all(slots.map((slot) => this.#renderSlot(slot, activities)));
  }

  async #renderSlot(slot, activities) {
    if (this.renderedSlots.has(slot) || this.pendingSlots.has(slot)) {
      return;
    }
    this.pendingSlots.add(slot);

    try {
      const matchingActivities = activities.filter(
        (activity) => activity.slot_id === slot.dataset.activitySlot,
      );
      const pageActivities = createPageActivities(slot.ownerDocument);
      let renderedActivityCount = 0;

      for (const activity of matchingActivities) {
        const renderer = this.renderers.get(activity.type);
        if (!renderer) {
          console.warn(`Brak renderera aktywności typu ${activity.type}.`);
          continue;
        }
        pageActivities.content.append(
          await renderer({
            activity,
            store: this.store,
            document: slot.ownerDocument,
          }),
        );
        renderedActivityCount += 1;
      }

      slot.replaceChildren(
        ...(renderedActivityCount > 0 ? [pageActivities.root] : []),
      );
      this.renderedSlots.add(slot);
    } finally {
      this.pendingSlots.delete(slot);
    }
  }
}
