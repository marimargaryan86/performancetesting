export type NoNever<
  T extends Record<string, unknown>,
  U extends keyof T = {
    [K in keyof T]: T[K] extends never ? never : K;
  }[keyof T],
  V = {
    [K in U]: T[K] extends Record<string, unknown>
      ? { [K2 in keyof NoNever<T[K]>]: NoNever<T[K]>[K2] }
      : T[K];
  },
> = V;

export type AddQuestionMarks<
  T extends Record<string, unknown>,
  A extends keyof T = {
    [K in keyof T]: undefined extends T[K] ? K : never;
  }[keyof T],
  B extends keyof T = Exclude<keyof T, A>,
  U = { [K in B]: T[K] } & { [K in A]?: T[K] },
  X = {
    [K in keyof U]: U[K] extends Record<string, unknown>
      ? { [K2 in keyof AddQuestionMarks<U[K]>]: AddQuestionMarks<U[K]>[K2] }
      : U[K];
  },
> = X;

export type Require<
  T extends Record<string, unknown>,
  A extends keyof T = never,
  B extends keyof T = Exclude<keyof T, A>,
  U = { [K in A]-?: Exclude<T[K], undefined> } & { [K in B]: T[K] },
  V = { [K in keyof U]: U[K] },
> = V;

export type Partialize<
  T extends Record<string, unknown>,
  A extends keyof T = never,
  B extends keyof T = Exclude<keyof T, A>,
  U = { [K in A]?: Exclude<T[K], undefined> } & { [K in B]: T[K] },
  V = { [K in keyof U]: U[K] },
> = V;

export type DeepPartial<
  T extends Record<string, unknown>,
  U = {
    [K in keyof T]?: T[K] extends Record<string, unknown> ? DeepPartial<T[K]> : T[K];
  },
> = U;

export type DeepRequired<
  T extends Record<string, unknown>,
  U = {
    [K in keyof T]-?: Exclude<
      T[K] extends Record<string, unknown> ? DeepRequired<T[K]> : T[K],
      undefined
    >;
  },
> = U;

export type Merge<
  T extends Record<string, unknown>,
  U extends Record<string, unknown>,
  TK extends keyof T = Exclude<keyof T, keyof U>,
  TU extends keyof U = Exclude<keyof U, TK>,
  V = { [K in TK]: T[K] } & { [K in TU]: U[K] },
  X = { [K in keyof V]: V[K] },
> = X;

export type FlattenKeys<T extends Record<string, unknown>> = {
  [K in keyof T]: K extends string | number
    ? `${K}${T[K] extends Record<string, unknown> ? `.${FlattenKeys<T[K]>}` : ""}`
    : never;
}[keyof T];
