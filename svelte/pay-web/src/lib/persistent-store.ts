import { writable as svelteWritable, type Writable } from "svelte/store";
import storage, { type StorageType } from "./storage";

type PersistentStore<TValue> = Writable<TValue> & { reset: () => void };
type GetWritableReturnType = <TValue>(
  id: string,
  valueGenerator: () => TValue,
  deserialize?: (value: TValue) => TValue,
) => PersistentStore<TValue>;

function getWritable(storageType: StorageType): GetWritableReturnType {
  return <TValue>(
    id: string,
    valueFactory: () => TValue,
    deserialize?: (value: TValue) => TValue,
  ): PersistentStore<TValue> => {
    let data: TValue;

    try {
      data = storage[storageType].get(id, deserialize);
    } catch {
      data = valueFactory();
    }

    const store = svelteWritable(data);

    store.subscribe((value: TValue) => {
      try {
        storage[storageType].put(id, value);
      } catch {
        //
      }
    });

    return {
      ...store,
      reset() {
        store.set(valueFactory());
      },
    };
  };
}

export default {
  writableSession: getWritable("session"),
  writableLocal: getWritable("local"),
};
