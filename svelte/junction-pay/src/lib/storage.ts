export type StorageType = "local" | "session";

function storageFromType(storage: StorageType): Storage {
  if (typeof window === "undefined") {
    throw new Error("Storage is not defined");
  }

  return storage === "local" ? localStorage : sessionStorage;
}

function put<TValue>(storageType: StorageType, id: string, value: TValue): TValue {
  const storage = storageFromType(storageType);

  storage.setItem(id, JSON.stringify(value));

  return value;
}

function get<TValue, TRaw>(
  storageType: StorageType,
  id: string,
  deserialize?: (value: TRaw) => TValue,
): TValue {
  const storage = storageFromType(storageType);
  const stringData = storage.getItem(id);

  if (!stringData) {
    throw new Error("Item not found");
  }

  const data = JSON.parse(stringData);

  return deserialize?.(data) ?? data;
}

function remove(storageType: StorageType, id: string): void {
  const storage = storageFromType(storageType);

  storage.removeItem(id);
}

function getStorage(storage: StorageType): {
  put: <TValue>(id: string, value: TValue) => TValue;
  get: <TValue, TRaw>(id: string, deserialize?: (value: TRaw) => TValue) => TValue;
  remove: (id: string) => void;
} {
  return {
    put<TValue>(id: string, value: TValue): TValue {
      return put(storage, id, value);
    },
    get<TValue, TRaw>(id: string, deserialize?: (value: TRaw) => TValue): TValue {
      return get(storage, id, deserialize);
    },
    remove(id: string): void {
      remove(storage, id);
    },
  };
}

export default {
  local: getStorage("local"),
  session: getStorage("session"),
};
