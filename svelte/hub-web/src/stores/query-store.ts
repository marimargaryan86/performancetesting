import { browser } from "$app/environment";
import { goto } from "$app/navigation";
import { page } from "$app/stores";
import { writable, type Writable } from "svelte/store";

type StoreSetter = (value: Record<string, string>, navigate?: boolean) => void;

function parseSearchParams(params: URLSearchParams): Record<string, string> {
  return Object.fromEntries(
    Object.entries(Object.fromEntries(params)).filter(([, val]) => val.length),
  );
}

function parseSearchString(search: string): Record<string, string> {
  return parseSearchParams(new URLSearchParams(search));
}

function queryStore(): Writable<Record<string, string>> {
  const store = writable<Record<string, string>>(parseSearchString(window.location.search), () =>
    page.subscribe(({ url }) => {
      if (!url) {
        return;
      }

      (store.set as StoreSetter)(parseSearchParams(url.searchParams), false);
    }),
  );

  const { set } = store;

  store.set = (value: Record<string, string>, navigate = true): void => {
    if (!navigate) {
      return set(value);
    }

    const { pathname, origin } = window.location;
    const url = new URL(pathname, origin);

    Object.entries(value).forEach(([key, val]) => {
      if (val.length) {
        url.searchParams.set(key, val);
      }
    });

    goto(url, { keepFocus: true, noScroll: true, replaceState: true });
  };

  return store;
}

/**
 * A Svelte store that synchronizes URL query parameters with application
 * state. It reads and writes to the URL's query parameters, updating itself
 * based on URL changes and also updates the URL when its values change.
 *
 * An empty string is treated as `undefined` and removes that key from the URL
 * query parameters.
 *
 * @example
 * // Binding a text input to a query parameter
 * <input type="text" bind:value={$queryStore.username} />
 *
 * // Navigating to `/?username=someone` will prefill the input with "someone".
 * // Typing in the input will update the URL's query parameter accordingly.
 */
export default browser ? queryStore() : writable<Record<string, string>>({});
