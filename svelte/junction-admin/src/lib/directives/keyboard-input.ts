export default function keyboardInput(
  node: Element,
  bindings: Record<string, () => void>,
): SvelteActionReturnType {
  let bindings_ = bindings;

  function keydown(e: KeyboardEvent): void {
    const func = bindings_[e.code];

    if (func) {
      e.preventDefault();
      func();
    }
  }

  node.addEventListener("keydown", keydown);

  return {
    destroy() {
      node.removeEventListener("keydown", keydown);
    },
    update(bindings) {
      bindings_ = bindings;
    },
  };
}
