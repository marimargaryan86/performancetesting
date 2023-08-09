import type { ActionReturn } from "svelte/action";

export function clickOutside(node: HTMLElement, func: () => void): ActionReturn {
  function onClick(event: MouseEvent): void {
    if (!node.contains(event.target as Node)) {
      func();
    }
  }

  window.addEventListener("click", onClick);

  return {
    destroy(): void {
      window.removeEventListener("click", onClick);
    },
  };
}
