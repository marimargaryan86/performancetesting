import type { MaybePromise } from "@sveltejs/kit";
import type { ActionReturn } from "svelte/action";

export type ScrollLoadFunc = () => MaybePromise<{ depleted: boolean }>;

interface ScrollLoadParams {
  threshold?: number;
  func?: ScrollLoadFunc;
}

const DEFAULT_THRESHOLD = 400;

export function scrollLoad(
  node: HTMLElement,
  params: ScrollLoadParams,
): ActionReturn<ScrollLoadParams> {
  let { func, threshold = DEFAULT_THRESHOLD } = params;
  let pending = false;
  let destroyed = false;

  async function onScroll(): Promise<void> {
    if (destroyed || !func) {
      return;
    }

    const delta = node.scrollHeight - (node.scrollTop + node.clientHeight);

    if (delta < threshold) {
      if (pending) {
        return;
      }

      pending = true;
      const result = await func();
      pending = false;

      // Trigger an additional onScroll in case the container isn't fully populated
      if (!result.depleted) {
        await onScroll();
      }
    }
  }

  node.addEventListener("scroll", onScroll);

  // Trigger an initial onScroll in case the container isn't fully populated
  onScroll();

  return {
    destroy(): void {
      destroyed = true;
      node.removeEventListener("scroll", onScroll);
    },
    update(p): void {
      ({ func, threshold = DEFAULT_THRESHOLD } = p);
    },
  };
}
