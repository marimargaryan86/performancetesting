import { dev } from "$app/environment";
import { error, type RequestEvent } from "@sveltejs/kit";
import * as jwt from "jsonwebtoken";
import { env } from "$env/dynamic/private";
import type { SessionExtended } from "integration/ory/schemas";

const SESSION_TOKEN = "session-token";
const COOKIE_OPTIONS = {
  path: "/",
  httpOnly: true,
  secure: !dev,
};
// Two weeks, as set by the Legal team. Do not modify.
const EXPIRY_MAX_AGE = 1209600;

export function getSession(event: RequestEvent): SessionExtended {
  const token = event.cookies.get(SESSION_TOKEN);

  try {
    if (token) {
      const data = jwt.verify(token, env.JWT_SECRET ?? "secret") as SessionExtended;
      return { ...data, expiresAt: new Date(data.expiresAt) };
    }
  } catch (err) {
    //
  }

  throw error(401, "Unauthorized");
}

export function setSession({
  session,
  rememberMe = false,
  event,
}: {
  session: SessionExtended;
  rememberMe?: boolean;
  event: RequestEvent;
}): void {
  const token = jwt.sign(session, env.JWT_SECRET ?? "secret", {});

  event.cookies.set(SESSION_TOKEN, token, {
    ...COOKIE_OPTIONS,
    maxAge: rememberMe ? EXPIRY_MAX_AGE : undefined,
  });
}

export function deleteSession(event: RequestEvent): void {
  event.cookies.delete(SESSION_TOKEN, COOKIE_OPTIONS);
}
