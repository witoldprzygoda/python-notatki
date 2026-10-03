import { createActivityShell } from "../activity-dom.js";


function clearMessage(message) {
  message.textContent = "";
  message.hidden = true;
}


function showTechnicalError(message, text) {
  message.className =
    "interactive-activity__message interactive-activity__message--error";
  message.textContent = `Błąd techniczny: ${text}`;
  message.hidden = false;
}


export async function renderAcknowledgement({ activity, store, document }) {
  const shell = createActivityShell({
    document,
    activity,
    type: "acknowledgement",
    typeLabel: "Potwierdzenie",
    title: activity.label,
    prompt:
      "Po zapoznaniu się z powyższym opisem oznacz aktywność jako wykonaną.",
  });

  const fieldset = document.createElement("fieldset");
  fieldset.className = "interactive-activity__fieldset";
  fieldset.setAttribute("aria-describedby", shell.promptId);

  const legend = document.createElement("legend");
  legend.className = "interactive-activity__visually-hidden";
  legend.textContent = "Potwierdzenie wykonania aktywności";

  const label = document.createElement("label");
  label.className =
    "interactive-activity__option interactive-activity__confirmation";
  const checkbox = document.createElement("input");
  checkbox.type = "checkbox";
  const labelText = document.createElement("span");
  labelText.textContent = "Oznacz jako wykonane";
  label.append(checkbox, labelText);

  const message = document.createElement("p");
  message.className = "interactive-activity__message";
  message.setAttribute("aria-live", "polite");
  message.setAttribute("aria-atomic", "true");
  message.hidden = true;

  try {
    const savedState = await store.get(activity.activity_id);
    checkbox.checked = savedState?.status === "completed";
    shell.setProgressState(checkbox.checked ? "completed" : "pending");
  } catch (error) {
    checkbox.disabled = true;
    shell.setProgressState("unknown");
    showTechnicalError(
      message,
      "nie można odczytać lokalnego stanu aktywności.",
    );
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
      shell.setProgressState(checkbox.checked ? "completed" : "pending");
      clearMessage(message);
    } catch (error) {
      checkbox.checked = !requestedState;
      showTechnicalError(
        message,
        "nie udało się zapisać lokalnego stanu aktywności.",
      );
      console.warn("Nie udało się zapisać postępu aktywności.", error);
    } finally {
      checkbox.disabled = false;
    }
  });

  fieldset.append(legend, label);
  shell.interaction.append(fieldset);
  shell.messages.append(message);
  return shell.root;
}
