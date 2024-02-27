export function clickOutside(node: HTMLElement, handler: () => void): { destroy: () => void } {
  const onClick = (event: MouseEvent): boolean | void =>
    node && !node.contains(event.target as HTMLElement) && !event.defaultPrevented && handler();

  document.addEventListener("click", onClick, true);

  return {
    destroy(): void {
      document.removeEventListener("click", onClick, true);
    },
  };
}
