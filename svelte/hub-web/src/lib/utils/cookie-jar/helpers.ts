import type { CookieOptions } from "./types";

export const SECURE_PREFIX = "__Secure-";

export function getCookieName(name: string, opts: Pick<CookieOptions, "secure">): string {
  return opts.secure ? `${SECURE_PREFIX}${name}` : name;
}
