import { writable, type StartStopNotifier, type Writable, type Readable } from "svelte/store";
import * as devalue from "devalue";
import { deleteCookie, getCookie, setCookie } from "./cookies";

type VerificationFunc<T> = (data: T) => boolean;

type WritableStorage<T> = Writable<T> & {
  /** Removes the item from storage. */
  remove: () => void;
};

interface StoreOptions<T> {
  key: string;
  value?: T;
  start?: StartStopNotifier<T>;
  verify?: VerificationFunc<T>;
}

function writableStorage<T>(
  options: StoreOptions<T> & {
    storageType: "localStorage" | "sessionStorage";
  },
): WritableStorage<T> {
  const store = writable(options.value, options.start);
  const returnValue = {
    ...store,
    remove(): void {
      //
    },
  };

  if (typeof window === "undefined") {
    return returnValue;
  }

  const storage = window[options.storageType];

  if (!storage) {
    return returnValue;
  }

  const initialValue = storage.getItem(options.key);

  if (initialValue) {
    const data = devalue.parse(initialValue);

    if (options.verify?.(data) ?? true) {
      store.set(data);
    } else {
      storage.removeItem(options.key);
    }
  }

  store.subscribe((value) => {
    storage.setItem(options.key, devalue.stringify(value));
  });

  return {
    ...store,
    remove(): void {
      storage?.removeItem(options.key);
    },
  };
}

export function writableLocalStorage<T>(options: StoreOptions<T>): WritableStorage<T> {
  return writableStorage({
    storageType: "localStorage",
    ...options,
  });
}

export function readableLocalStorage<T>(options: StoreOptions<T>): Readable<T> {
  return writableLocalStorage(options);
}

export function writableSessionStorage<T>(options: StoreOptions<T>): WritableStorage<T> {
  return writableStorage({
    storageType: "sessionStorage",
    key: options.key,
    start: options.start,
    value: options.value,
    verify: options.verify,
  });
}

export function readableSessionStorage<T>(options: StoreOptions<T>): Readable<T> {
  return writableSessionStorage(options);
}

export function writableCookie<T>(options: StoreOptions<T>): WritableStorage<T> {
  const store = writable(options.value, options.start);
  const returnValue = {
    ...store,
    remove(): void {
      //
    },
  };

  if (typeof window === "undefined") {
    return returnValue;
  }

  const cookieValue = getCookie(options.key);

  if (cookieValue) {
    const data = devalue.parse(decodeURIComponent(window.atob(cookieValue)));

    if (options.verify?.(data) ?? true) {
      store.set(data);
    } else {
      deleteCookie(options.key);
    }
  }

  store.subscribe((value) => {
    setCookie(options.key, window.btoa(encodeURIComponent(devalue.stringify(value))));
  });

  return {
    ...store,
    remove(): void {
      deleteCookie(options.key);
    },
  };
}

export function readableCookie<T>(options: StoreOptions<T>): Readable<T> {
  return writableCookie(options);
}
