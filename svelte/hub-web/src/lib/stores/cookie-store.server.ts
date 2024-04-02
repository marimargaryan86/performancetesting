import { dev } from "$app/environment";
import { env } from "$env/dynamic/private";
import type { RequestEvent } from "@sveltejs/kit";
import type * as OrySchemas from "~/integration/ory/schemas";
import jwt from "jsonwebtoken";
import * as devalue from "devalue";

type CookieOptions = {
  path?: string;
  secure?: boolean;
  httpOnly?: boolean;
  sameSite?: boolean | "lax" | "strict" | "none";
  expires?: Date;
  domain?: string;
  maxAge?: number;
  priority?: "low" | "medium" | "high" | undefined;
};

type CookieOptionsOverride = Pick<CookieOptions, "expires" | "maxAge">;

function createCookie<TValue>(
  cookieName: string,
  {
    path = "/",
    secure = !dev,
    httpOnly = true,
    sameSite = "none",
    expires,
    domain,
    maxAge,
    priority,
  }: CookieOptions = {},
): {
  get(event: RequestEvent): TValue | undefined;
  set(value: TValue, event: RequestEvent, optionsOverride?: CookieOptionsOverride): string;
  delete(event: RequestEvent): void;
} {
  // Prefix with __Secure if it is secure
  // https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Set-Cookie#cookie_prefixes
  const name = secure ? `__Secure-${cookieName}` : cookieName;
  const options = { path, secure, httpOnly, sameSite, expires, domain, maxAge, priority };

  return {
    get: (event): TValue | undefined => {
      const value = event.cookies.get(name);

      if (!value) {
        return undefined;
      }

      try {
        // JSON.stringify since jsonwebtoken doesn't allow a custom parser.
        return devalue.parse(JSON.stringify(jwt.verify(value, env.JWT_SECRET as string)));
      } catch {
        return undefined;
      }
    },
    set: (value, event, optionsOverride): string => {
      const encoded = jwt.sign(devalue.stringify(value), env.JWT_SECRET as string);

      event.cookies.set(name, encoded, {
        ...options,
        ...optionsOverride,
      });

      return encoded;
    },
    delete: (event): void => {
      event.cookies.delete(name, options);
    },
  };
}

export const cookieStore = {
  loginToken: createCookie<{ id: string; cookies: Record<string, string> }>("login-token"),
  recoveryToken: createCookie<{ id: string; cookies: Record<string, string> }>("recovery-token"),
  userSettingsToken: createCookie<{ id: string; cookies: Record<string, string> }>(
    "user-settings-token",
  ),
  sessionToken: createCookie<OrySchemas.Session>("session-token"),
  sessionMetaToken: createCookie<OrySchemas.SessionMeta>("session-meta-token"),
};
