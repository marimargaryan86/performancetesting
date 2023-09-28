import { error, type RequestEvent } from "@sveltejs/kit";
import type { SessionModel } from "models/user";

const SESSION_TOKEN = "session-token";
const SESSION_ID = "session-id";

export function getSession(event: RequestEvent): SessionModel {
  const id = event.cookies.get(SESSION_ID);
  const token = event.cookies.get(SESSION_TOKEN);

  if (id && token) {
    return { id, token };
  }

  throw error(401, "Unauthorized");
}

export function setSession(id: string, token: string, event: RequestEvent): void {
  event.cookies.set(SESSION_ID, id, { path: "/", httpOnly: true, sameSite: "strict" });
  event.cookies.set(SESSION_TOKEN, token, { path: "/", httpOnly: true, sameSite: "strict" });
}

export function deleteSession(event: RequestEvent): void {
  event.cookies.delete(SESSION_ID, { path: "/", httpOnly: true, sameSite: "strict" });
  event.cookies.delete(SESSION_TOKEN, { path: "/", httpOnly: true, sameSite: "strict" });
}
