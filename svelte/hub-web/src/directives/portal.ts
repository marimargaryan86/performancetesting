export function portal(node: HTMLElement, target: HTMLElement): void {
  node.parentNode?.removeChild(node);
  target.appendChild(node);
}
