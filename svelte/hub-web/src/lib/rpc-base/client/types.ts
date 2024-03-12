import type { Callable, ClientCallable } from "../types";

export type ClientMapping<TServerMethods extends object> = Partial<
  Record<keyof TServerMethods, ClientCallable>
>;

export type ClientMethods<
  TServerMethods extends object,
  TClientMapping extends ClientMapping<TServerMethods>,
> = {
  [key in keyof (TServerMethods | TClientMapping)]: TServerMethods[key] extends Callable
    ? TClientMapping[key] extends ClientCallable
      ? (
          ...args: Parameters<TClientMapping[key]>
        ) => Promise<Awaited<ReturnType<TServerMethods[key]>>>
      : never
    : never;
};
