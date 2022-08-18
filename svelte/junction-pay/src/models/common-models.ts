export type ValidationError<TData extends Record<string, unknown>> = Partial<
  Record<keyof TData, string[]>
>;

export type LocalStorageWithExpiry = {
  value: string;
  expiry: Date;
};
