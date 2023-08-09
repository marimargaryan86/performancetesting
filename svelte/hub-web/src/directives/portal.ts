import type { ActionReturn } from "svelte/action";

export function portal(node: HTMLElement, target: HTMLElement): ActionReturn {
  node.parentNode?.removeChild(node);
  target.appendChild(node);

  return {};
}
