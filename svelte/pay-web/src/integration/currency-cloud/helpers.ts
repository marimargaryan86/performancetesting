export function patchObject<T, U>(target: T, update: U | undefined): T {
  if (update === undefined) {
    return target;
  }

  if (target instanceof Array) {
    if (update instanceof Array) {
      return update as unknown as T;
    }

    return target;
  }

  if (typeof target === "object" && typeof update === "object") {
    return Object.fromEntries(
      Object.entries(target).map(([key, value]) => {
        const newValue = update[key as keyof U];

        if (newValue === undefined) {
          return [key, value];
        }

        return [key, patchObject(value, newValue)];
      }),
    ) as T;
  }

  return (update === undefined ? target : update) as T;
}

export function removeUndefinedValues<T>(obj: T, treatEmptyAsUndefined = true): T | undefined {
  if (obj instanceof Array) {
    const result = obj
      .map((item) => removeUndefinedValues(item, treatEmptyAsUndefined))
      .filter((item) => item !== undefined);

    return !result.length && treatEmptyAsUndefined ? undefined : (result as unknown as T);
  }

  if (typeof obj === "function") {
    return obj;
  }

  if (typeof obj === "object") {
    const result = Object.fromEntries(
      Object.entries(obj)
        .map(([key, value]) => [key, removeUndefinedValues(value, treatEmptyAsUndefined)])
        .filter(([, value]) => value !== undefined),
    );

    return !Object.keys(result).length && treatEmptyAsUndefined
      ? undefined
      : (result as unknown as T);
  }

  return obj;
}

export function thisOrThat<T>(value1: T | null, value2: T): T | null {
  if (value1 === undefined) {
    return value2;
  }

  return value1;
}
