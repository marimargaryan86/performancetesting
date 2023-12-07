import { browser } from "$app/environment";
import { goto } from "$app/navigation";
import { page } from "$app/stores";
import type { Unsubscriber } from "svelte/motion";
import { get, writable } from "svelte/store";

/**
 * A Svelte store that synchronizes URL query parameters with application
 * state. It reads and writes to the URL's query parameters, updating itself
 * based on URL changes and also updates the URL when its values change.
 *
 * A trimmed `""` is treated as `undefined` and removes that key from the URL
 * query parameters.
 *
 * @example
 * // Binding a text input to a query parameter
 * <input type="text" bind:value={$queryStore.username} />
 *
 * // Navigating to `/?username=someone` will prefill the input with "someone".
 * // Typing in the input will update the URL's query parameter accordingly.
 */
const queryStore = writable<Record<string, string | undefined>>(
  {},
  browser
    ? (): Unsubscriber => {
        const unsubscribe = page.subscribe(({ url }) => {
          if (url) {
            queryStore.set(Object.fromEntries(url.searchParams));
          }
        });

        return unsubscribe;
      }
    : undefined,
);

if (browser) {
  queryStore.subscribe((value) => {
    const { url } = get(page);

    Object.entries(value).forEach(([key, val]) => {
      if (val?.trim().length) {
        url.searchParams.set(key, val.trim());
      } else {
        url.searchParams.delete(key);
      }

      if (browser) {
        goto(url, { keepFocus: true, noScroll: true, replaceState: true });
      }
    });
  });
}

export default queryStore;
