export type ValidationError<TData extends Record<string, unknown>> = Partial<
  Record<keyof TData, string[]>
>;
