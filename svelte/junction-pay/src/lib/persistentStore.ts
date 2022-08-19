import { writable as svelteWritable, type Writable } from "svelte/store";
import storage, { type StorageType } from "./storage";

function getWritable(
  storageType: StorageType,
): <TValue, TRaw = unknown>(
  id: string,
  value?: TValue,
  deserialize?: (value: TRaw) => TValue,
) => Writable<TValue> {
  return <TValue, TRaw>(
    id: string,
    value?: TValue,
    deserialize?: (value: TRaw) => TValue,
  ): Writable<TValue> => {
    let data: TValue;

    try {
      data = storage[storageType].get(id, deserialize);
    } catch {
      if (value === undefined) {
        throw new Error(`No default store value for ${id}`);
      }

      data = value;
    }

    const store = svelteWritable(data);

    store.subscribe((value: TValue) => {
      try {
        storage[storageType].put(id, value);
      } catch {
        //
      }
    });

    return store;
  };
}

export default {
  writableSession: getWritable("session"),
  writableLocal: getWritable("local"),
};
