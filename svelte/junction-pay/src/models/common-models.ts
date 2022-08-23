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

export type LocalStorageWithExpiry = {
  value: string;
  expiry: Date;
};
