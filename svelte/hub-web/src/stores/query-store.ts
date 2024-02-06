import { goto } from "$app/navigation";
import { getContext, setContext } from "svelte";
import { get, writable, type Writable } from "svelte/store";
import { URLExtended } from "~/utils/url";

/**
 * Set the query store context
 * @param searchParams Initial search params
 */
export function setQueryStore(
  searchParams: URLSearchParams,
): Writable<Record<string, string | undefined>> {
  const store = writable(Object.fromEntries(searchParams));

  return setContext("queryStore", store);
}

/**
 * Get the query store context
 *
 * This store will add the values to the current URLs query parameters as it changes.
 * It debounces changes by 1000ms which is refreshed every time the store changes.
 *
 * @param config Contains a `getter` for parsing query data into a model, a `setter` for parsing
 * a model into query data and an optional validator for the model. If the validator returns false
 * for any field when the store updates, no navigation will be performed.
 */
export function getQueryStore<
  TData extends Record<string, unknown>,
  TQuery extends Record<string, string | undefined>,
>(config: {
  get: (value: TQuery) => TData;
  set: (value: TData) => TQuery;
  valid?: (value: TData) => { [key in keyof TData]?: boolean };
}): Writable<TData> {
  const store = getContext<Writable<TQuery>>("queryStore");
  const result = writable(config.get(get(store)), (set) =>
    store.subscribe((value) => set(config.get(value))),
  );

  let triggered = new Date().getTime();

  result.set = (value: TData): void => {
    const curr = new Date().getTime();
    triggered = curr;
    const validated: { [key in keyof TData]?: boolean } = config.valid?.(value) ?? {};
    const valid = !Object.values(validated).includes(false);

    if (!valid) {
      return;
    }

    setTimeout(() => {
      if (curr !== triggered) {
        return;
      }

      goto(
        new URLExtended(window.location.pathname, {
          base: window.location.origin,
          query: config.set(value),
        }),
        { keepFocus: true, noScroll: true, replaceState: true, invalidateAll: false },
      );
    }, 1000);
  };

  return result;
}
