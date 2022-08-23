export default function keyBinding<Params extends Record<string, (() => void) | undefined>>(
  node: HTMLElement,
  mapping: Params,
): SvelteActionReturnType {
  let mapping_ = mapping;

  function keyDown(ev: KeyboardEvent): void {
    const func = mapping_[ev.code];

    if (func) {
      ev.preventDefault();
      func();
    }
  }

  node.addEventListener("keydown", keyDown);

  return {
    destroy() {
      node.removeEventListener("keydown", keyDown);
    },
    update(mapping: Params) {
      mapping_ = mapping;
    },
  };
}
