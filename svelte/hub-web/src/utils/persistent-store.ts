import { writable, type StartStopNotifier, type Writable } from "svelte/store";
import * as devalue from "devalue";

type WritableStorage<T> = Writable<T> & {
  /** Removes the item from storage. */
  remove: () => void;
};

function writableStorage<T>({
  storage: storageKey,
  key,
  value,
  start,
}: {
  storage: "localStorage" | "sessionStorage";
  key: string;
  value?: T;
  start?: StartStopNotifier<T>;
}): WritableStorage<T> {
  const storage = typeof window === "undefined" ? undefined : window[storageKey];
  const storageValue = storage?.getItem(key);
  const initialValue = typeof storageValue === "string" ? devalue.parse(storageValue) : value;
  const store = writable(initialValue, start);

  store.subscribe((nextValue) => {
    storage?.setItem(key, devalue.stringify(nextValue));
  });

  return {
    ...store,
    remove(): void {
      storage?.removeItem(key);
    },
  };
}

export function writableLocal<T>(
  key: string,
  value?: T,
  start?: StartStopNotifier<T>,
): WritableStorage<T> {
  return writableStorage({ storage: "localStorage", key, value, start });
}

export function writableSession<T>(
  key: string,
  value?: T,
  start?: StartStopNotifier<T>,
): WritableStorage<T> {
  return writableStorage({ storage: "sessionStorage", key, value, start });
}
