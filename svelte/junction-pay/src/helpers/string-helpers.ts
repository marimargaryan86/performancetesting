export function undefinedIfZeroLength<T>(value?: T): NonNullable<T> | undefined {
  const valueWithLength = value as unknown as { length: number };

  if (!valueWithLength?.length) {
    return undefined;
  }

  return value ?? undefined;
}
