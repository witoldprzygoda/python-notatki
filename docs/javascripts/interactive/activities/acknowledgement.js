function setStatus(statusElement, completed) {
  statusElement.textContent = completed
    ? "Status: wykonano."
    : "Status: do wykonania.";
}


export async function renderAcknowledgement({ activity, store, document }) {
  const fieldset = document.createElement("fieldset");
  fieldset.className = "interactive-activity interactive-activity--acknowledgement";
  fieldset.dataset.activityId = activity.activity_id;

  const legend = document.createElement("legend");
  legend.textContent = "Potwierdzenie zapoznania się z materiałem";

  const instruction = document.createElement("p");
  instruction.textContent =
    "Po zapoznaniu się z powyższym opisem zaznacz poniższe pole.";

  const label = document.createElement("label");
  const checkbox = document.createElement("input");
  checkbox.type = "checkbox";
  const labelText = document.createElement("span");
  labelText.textContent = activity.label;
  label.append(checkbox, document.createTextNode(" "), labelText);

  const status = document.createElement("p");
  status.setAttribute("aria-live", "polite");

  try {
    const savedState = await store.get(activity.activity_id);
    checkbox.checked = savedState?.status === "completed";
    setStatus(status, checkbox.checked);
  } catch (error) {
    checkbox.disabled = true;
    status.textContent = "Nie można odczytać lokalnego stanu aktywności.";
    console.warn("Nie udało się odczytać postępu aktywności.", error);
  }

  checkbox.addEventListener("change", async () => {
    const requestedState = checkbox.checked;
    checkbox.disabled = true;

    try {
      const savedState = await store.save(activity.activity_id, {
        version: activity.version,
        status: requestedState ? "completed" : "not_started",
      });
      checkbox.checked = savedState.status === "completed";
      setStatus(status, checkbox.checked);
    } catch (error) {
      checkbox.checked = !requestedState;
      status.textContent = "Nie udało się zapisać lokalnego stanu aktywności.";
      console.warn("Nie udało się zapisać postępu aktywności.", error);
    } finally {
      checkbox.disabled = false;
    }
  });

  fieldset.append(legend, instruction, label, status);
  return fieldset;
}
