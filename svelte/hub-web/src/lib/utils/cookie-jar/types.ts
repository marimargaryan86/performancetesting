import type { CookieParseOptions, CookieSerializeOptions } from "cookie";

export type CookieOptions = CookieParseOptions & CookieSerializeOptions;

export type GetCookieOptions = Pick<CookieOptions, "decode" | "secure">;

export type SetCookieOptions = Omit<CookieOptions, "decode">;

export type DeleteCookieOptions = Omit<SetCookieOptions, "expires" | "maxAge">;

export type CookieJar = {
  get(name: string, opts?: GetCookieOptions): string | undefined;
  set(name: string, value: string, options?: SetCookieOptions): void;
  delete(name: string, options?: DeleteCookieOptions): void;
};
