import type { BeneficiaryWizardComplete } from "$models/beneficiary-models";
import type { ModalParams } from "$models/modal-models";
import { writable } from "svelte/store";

export const wizardStore = createWizardStore();

function createWizardStore() {
  const { subscribe, set, update } = writable<Partial<BeneficiaryWizardComplete>>({});

  function addDetails(data: Partial<BeneficiaryWizardComplete>) {
    update((state) => {
      state = {
        ...state,
        ...data,
      };
      return state;
    });
  }

  return {
    subscribe,
    addDetails,
    reset: () => set({}),
  };
}

export const modal = writable<ModalParams>({
  status: "closed", // opened | closed,
  type: "info",
  component: undefined,
  title: "",
  options: {},
});

export function openPopup(params: ModalParams): void {
  modal.set({
    ...params,
    status: "open",
  });
}

export function close() {
  modal.set({
    status: "closed",
    type: "modal",
    title: "",
    component: undefined,
    options: {},
    firstFocusElement: undefined,
  });
}
