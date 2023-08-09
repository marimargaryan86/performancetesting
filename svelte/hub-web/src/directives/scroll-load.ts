import type { ActionReturn } from "svelte/action";

interface ScrollLoadParams {
  threshold?: number;
  func?: () => Promise<void> | void;
}

const DEFAULT_THRESHOLD = 400;

export function scrollLoad(
  node: HTMLElement,
  params: ScrollLoadParams,
): ActionReturn<ScrollLoadParams> {
  let { func, threshold = DEFAULT_THRESHOLD } = params;
  let pending = false;

  async function onScroll(): Promise<void> {
    if (!func) {
      return;
    }

    const delta = node.scrollHeight - (node.scrollTop + node.clientHeight);

    if (delta < threshold) {
      if (pending) {
        return;
      }

      pending = true;
      await func();
      pending = false;
    }
  }

  node.addEventListener("scroll", onScroll);

  return {
    destroy(): void {
      node.removeEventListener("scroll", onScroll);
    },
    update(p): void {
      ({ func, threshold = DEFAULT_THRESHOLD } = p);
    },
  };
}
