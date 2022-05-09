export default function clickOutside(node: Element, action: () => void): SvelteActionReturnType {
  let action_ = action;

  function click(e: MouseEvent): void {
    if (node.contains(e.target as Node)) {
      return;
    }

    action_();
  }

  window.addEventListener("mousedown", click);

  return {
    destroy() {
      window.removeEventListener("mousedown", click);
    },
    update(action: () => void) {
      action_ = action;
    },
  };
}
