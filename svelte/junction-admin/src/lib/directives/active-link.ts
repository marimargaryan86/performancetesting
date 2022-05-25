import { page } from "$app/stores";

export default function activeLink(node: HTMLAnchorElement, exact = true): SvelteActionReturnType {
  let _exact = exact;

  const unsubscriber = page.subscribe((page) => {
    const href = page.url.toString();

    if ((_exact && href === node.href) || (!_exact && href.startsWith(node.href))) {
      node.classList.add("active");
    } else {
      node.classList.remove("active");
    }
  });

  return {
    destroy() {
      unsubscriber();
    },
    update(exact) {
      _exact = exact;
    },
  };
}
