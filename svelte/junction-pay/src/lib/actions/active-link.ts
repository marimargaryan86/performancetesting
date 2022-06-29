import { page } from "$app/stores";

export default function activeLink(
  node: HTMLAnchorElement,
  { exact = true } = {},
): SvelteActionReturnType {
  let exact_ = exact;
  const { href } = node;

  const unsubscribe = page.subscribe((page) => {
    if (exact_ && page.url.href === href) {
      node.classList.add("active");
    } else if (!exact_ && page.url.href.startsWith(href)) {
      node.classList.add("active");
    } else {
      node.classList.remove("active");
    }
  });

  return {
    destroy() {
      unsubscribe();
    },
    update({ exact = true } = {}) {
      exact_ = exact;
    },
  };
}
