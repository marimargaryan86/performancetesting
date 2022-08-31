export type RecursivePartial<T> = {
  [P in keyof T]?: T[P] extends (infer U)[]
    ? RecursivePartial<U>[]
    : T[P] extends Date
    ? Date
    : T[P] extends object
    ? RecursivePartial<T[P]>
    : T[P];
};

export type ValidationError<T> = T extends object | undefined
  ?
      | {
          [P in keyof T]?: T[P] extends (infer U)[] | undefined
            ? Record<number, ValidationError<U>> | string[] | undefined
            : T[P] extends Date
            ? string[] | undefined
            : T[P] extends object | undefined
            ? ValidationError<T[P]>
            : string[] | undefined;
        }
      | undefined
  : string[] | undefined;
