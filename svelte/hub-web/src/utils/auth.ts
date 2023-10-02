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

export function getSession(event: RequestEvent): SessionModel {
  const id = event.cookies.get(SESSION_ID);
  const token = event.cookies.get(SESSION_TOKEN);

  if (id && token) {
    return { id, token };
  }

  throw error(401, "Unauthorized");
}

export function setSession(id: string, token: string, event: RequestEvent): void {
  event.cookies.set(SESSION_ID, id, COOKIE_OPTIONS);
  event.cookies.set(SESSION_TOKEN, token, COOKIE_OPTIONS);
}

export function deleteSession(event: RequestEvent): void {
  event.cookies.delete(SESSION_ID, COOKIE_OPTIONS);
  event.cookies.delete(SESSION_TOKEN, COOKIE_OPTIONS);
}
