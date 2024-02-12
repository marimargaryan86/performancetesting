import type { ActionReturn } from "svelte/action";

export type KeyboardParams = Record<string, (event: KeyboardEvent) => unknown>;

export function keyboard(node: HTMLElement, actions: KeyboardParams): ActionReturn<KeyboardParams> {
  let map = actions;

  function onKeyDown(event: KeyboardEvent): void {
    map[event.key]?.(event);
  }

  node.addEventListener("keydown", onKeyDown);

  return {
    destroy(): void {
      node.removeEventListener("keydown", onKeyDown);
    },
    update(nextActions: KeyboardParams): void {
      map = nextActions;
    },
  };
}
