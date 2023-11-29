import { dev } from "$app/environment";
import { env } from "$env/dynamic/private";
import type { RequestEvent } from "@sveltejs/kit";
import type { Session, SessionMeta } from "integration/ory/schemas/authentication";
import jwt from "jsonwebtoken";
import * as devalue from "devalue";
import type { BookingSessionModel } from "../routes/integration/trip-management/trip-management";

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
  name: string,
  {
    path = "/",
    secure = !dev,
    httpOnly = true,
    sameSite = "strict",
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
  const options = { path, secure, httpOnly, sameSite, expires, domain, maxAge, priority };

  return {
    get: (event): TValue | undefined => {
      const value = event.cookies.get(name);

      if (!value) {
        return undefined;
      }

      try {
        // JSON.stringify since jsonwebtoken doesn't allow a custom parser.
        return devalue.parse(JSON.stringify(jwt.verify(value, env.JWT_SECRET ?? "secret")));
      } catch {
        return undefined;
      }
    },
    set: (value, event, optionsOverride): string => {
      const encoded = jwt.sign(devalue.stringify(value), env.JWT_SECRET ?? "secret");

      event.cookies.set(name, encoded, { ...options, ...optionsOverride });

      return encoded;
    },
    delete: (event): void => {
      event.cookies.delete(name, options);
    },
  };
}

export const cookieStore = {
  loginToken: createCookie<Record<string, string>>("login-token"),
  recoveryToken: createCookie<{ id: string; cookies: Record<string, string> }>("recovery-token"),
  userSettingsToken: createCookie<{ id: string; cookies: Record<string, string> }>(
    "user-settings-token",
  ),
  sessionToken: createCookie<Session>("session-token"),
  sessionMetaToken: createCookie<SessionMeta>("session-meta-token"),
  searchToken: createCookie<BookingSessionModel>("search-token"),
};
