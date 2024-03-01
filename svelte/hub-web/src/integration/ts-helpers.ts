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

export type DeepPartial<T> = T extends
  | string
  | number
  | bigint
  | boolean
  | null
  | undefined
  | symbol
  | Date
  ? T | undefined
  : // eslint-disable-next-line no-inline-comments
    // Arrays, Sets and Maps and their readonly counterparts have their items made
    // deeply partial, but their own instances are left untouched
    T extends Array<infer ArrayType>
    ? Array<DeepPartial<ArrayType>>
    : T extends ReadonlyArray<infer ArrayType>
      ? ReadonlyArray<ArrayType>
      : T extends Set<infer SetType>
        ? Set<DeepPartial<SetType>>
        : T extends ReadonlySet<infer SetType>
          ? ReadonlySet<SetType>
          : T extends Map<infer KeyType, infer ValueType>
            ? Map<DeepPartial<KeyType>, DeepPartial<ValueType>>
            : T extends ReadonlyMap<infer KeyType, infer ValueType>
              ? ReadonlyMap<DeepPartial<KeyType>, DeepPartial<ValueType>>
              : // eslint-disable-next-line no-inline-comments
                // ...and finally, all other objects.
                {
                  [K in keyof T]?: DeepPartial<T[K]>;
                };

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
