import type { RequestEvent } from "@sveltejs/kit";
import { getCookieName } from "./helpers";
import type { CookieOptions, CookieJar } from "./types";

export function getSvelteKitCookieJar(
  event: RequestEvent,
  options: CookieOptions | undefined,
): CookieJar {
  return {
    get: (name, opts): string | undefined => {
      const finalOptions = { ...options, ...opts };

      return event.cookies.get(getCookieName(name, finalOptions), finalOptions);
    },
    set: (name, value, opts): void => {
      const finalOptions = {
        ...options,
        ...opts,
        path: opts?.path ?? options?.path ?? "/",
      };

      event.cookies.set(getCookieName(name, finalOptions), value, finalOptions);
    },
    delete: (name, opts): void => {
      const finalOptions = {
        ...options,
        ...opts,
        path: opts?.path ?? options?.path ?? "/",
      };

      event.cookies.delete(getCookieName(name, finalOptions), finalOptions);
    },
  };
}
