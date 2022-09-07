import type { SvelteComponent } from "svelte";

export type ModalState = "open" | "closed";

export type ModalOptions = {
  message?: string;
  showConfirmButton?: boolean;
  showCancelButton?: boolean;
  confirmText?: string;
  cancelText?: string;
  confirmFunction?: () => void;
  cancelFunction?: () => void;
};

export type ModalParams = {
  status?: ModalState;
  component?: SvelteComponent | undefined;
  type?: string;
  title: string;
  options?: ModalOptions;
  firstFocusElement?: HTMLElement;
};
