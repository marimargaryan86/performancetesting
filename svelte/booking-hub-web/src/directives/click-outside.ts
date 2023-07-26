export function clickOutside(node: HTMLElement, func: () => void): { destroy: () => void } {
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
