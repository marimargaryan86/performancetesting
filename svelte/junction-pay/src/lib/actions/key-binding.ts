export default function keyBinding<Params extends Record<string, () => void>>(
  node: HTMLElement,
  mapping: Params,
): SvelteActionReturnType {
  let mapping_ = mapping;

  function keyDown(ev: KeyboardEvent): void {
    mapping_[ev.code]?.();
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
