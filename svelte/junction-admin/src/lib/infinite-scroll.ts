import { writable, type Readable } from "svelte/store";

export type InfiniteScrollParams = {
  threshold?: number;
};

function isScrollBelowThreshold(node: Element, threshold: number): boolean {
  const height = node.getBoundingClientRect().height;
  const { scrollHeight, scrollTop } = node;

  return scrollHeight - (height + scrollTop) <= threshold;
}

function bindLoadTriggers(node: Element, exec: () => Promise<void>): () => void {
  node.addEventListener("scroll", exec);
  const resizeObserver = new ResizeObserver(exec);
  resizeObserver.observe(node);
  const mutationObserver = new MutationObserver(exec);
  mutationObserver.observe(node, { childList: true });

  return () => {
    node.removeEventListener("scroll", exec);
    resizeObserver.disconnect();
    mutationObserver.disconnect();
  };
}

export default function create<T = unknown>(
  load: (pageOffset: number, pageLimit: number) => Promise<T[]>,
  pageLimit: number,
): {
  items: Readable<T[]>;
  pending: Readable<boolean>;
  depleted: Readable<boolean>;
  infiniteScroll: (node: Element, params?: InfiniteScrollParams) => SvelteActionReturnType;
  reset: () => void;
} {
  const items = writable<T[]>([]);
  const pending = writable(false);
  const depleted = writable(false);

  let pageOffset = 0;
  let currTask: Promise<T[]>;

  function reset(): void {
    pageOffset = 0;
    currTask = undefined;
    pending.set(true);
    depleted.set(false);
    items.set([]);
    load_();
  }

  async function load_(): Promise<void> {
    if (currTask || pageOffset === -1) {
      // Cancel if there is an ongoing task or the result is depleted.
      return;
    }

    pending.set(true);
    depleted.set(false);

    const task = (currTask = load(pageOffset, pageLimit));
    const nextItems = await task;

    if (currTask !== task) {
      return;
    }

    pageOffset += 1;

    if (!nextItems.length) {
      pageOffset = -1;
    }

    pending.set(false);
    depleted.set(pageOffset === -1);
    items.update((state) => [...state, ...nextItems]);

    currTask = undefined;
  }

  function infiniteScroll(
    node: Element,
    { threshold = 300 }: InfiniteScrollParams = {},
  ): SvelteActionReturnType {
    let threshold_ = threshold;

    async function exec(): Promise<void> {
      if (!isScrollBelowThreshold(node, threshold_)) {
        return;
      }

      load_();
    }

    const unbindLoadTriggers = bindLoadTriggers(node, exec);

    return {
      destroy() {
        unbindLoadTriggers();
      },
      update({ threshold }: InfiniteScrollParams) {
        threshold_ = threshold;
      },
    };
  }

  return { items, pending, depleted, infiniteScroll, reset };
}
