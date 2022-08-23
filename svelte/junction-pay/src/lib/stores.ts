import type { ModalParams } from "$models/modal-models";
import { writable } from "svelte/store";

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
