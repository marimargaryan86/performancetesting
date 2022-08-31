export type RecursivePartial<T> = {
  [P in keyof T]?: T[P] extends (infer U)[]
    ? RecursivePartial<U>[]
    : T[P] extends object
    ? RecursivePartial<T[P]>
    : T[P];
};

export type ValidationError<T> = {
  [P in keyof T]?: string[] | undefined;
};

export type JSONCompatible<T> = {
  [P in keyof T]: T[P] extends (infer U)[]
    ? JSONCompatible<U>[]
    : T[P] extends Date
    ? string
    : T[P] extends object
    ? JSONCompatible<T[P]>
    : T[P];
};
