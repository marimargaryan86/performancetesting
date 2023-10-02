import { dev } from "$app/environment";
import { error, type RequestEvent } from "@sveltejs/kit";
import type { SessionModel } from "models/user";

const SESSION_TOKEN = "session-token";
const SESSION_ID = "session-id";
const COOKIE_OPTIONS = {
  path: "/",
  httpOnly: true,
  secure: !dev,
};
// Two weeks, as set by the Legal team. Do not modify.
const EXPIRY_MAX_AGE = 1209600;

export function getSession(event: RequestEvent): SessionModel {
  const id = event.cookies.get(SESSION_ID);
  const token = event.cookies.get(SESSION_TOKEN);

  if (id && token) {
    return { id, token };
  }

  throw error(401, "Unauthorized");
}

export function setSession({
  id,
  token,
  rememberMe = false,
  event,
}: {
  id: string;
  token: string;
  rememberMe?: boolean;
  event: RequestEvent;
}): void {
  event.cookies.set(SESSION_ID, id, {
    ...COOKIE_OPTIONS,
    maxAge: rememberMe ? EXPIRY_MAX_AGE : undefined,
  });
  event.cookies.set(SESSION_TOKEN, token, {
    ...COOKIE_OPTIONS,
    maxAge: rememberMe ? EXPIRY_MAX_AGE : undefined,
  });
}

export function deleteSession(event: RequestEvent): void {
  event.cookies.delete(SESSION_ID, COOKIE_OPTIONS);
  event.cookies.delete(SESSION_TOKEN, COOKIE_OPTIONS);
}
