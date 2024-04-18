import { parse, serialize } from "cookie";
import { getCookieName } from "./helpers";
import type { CookieOptions, CookieJar } from "./types";

export function getBrowserCookieJar(options: CookieOptions | undefined): CookieJar {
  return {
    get: (name, opts): string | undefined => {
      const finalOptions = { ...options, ...opts };

      return parse(document.cookie, finalOptions)[getCookieName(name, finalOptions)];
    },
    set: (name, value, opts): void => {
      const finalOptions = {
        ...options,
        ...opts,
        path: opts?.path ?? options?.path ?? "/",
      };

      document.cookie = serialize(getCookieName(name, finalOptions), value, finalOptions);
    },
    delete: (name, opts): void => {
      const finalOptions = {
        ...options,
        ...opts,
        path: opts?.path ?? options?.path ?? "/",
        expires: new Date(0),
      };

      document.cookie = serialize(getCookieName(name, finalOptions), "", finalOptions);
    },
  };
}
