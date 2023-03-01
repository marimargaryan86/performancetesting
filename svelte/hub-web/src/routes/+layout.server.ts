import type { ServerLoadEvent } from "@sveltejs/kit";

export function load(event: ServerLoadEvent): { loggedIn: boolean } {
  const token = event.cookies.get("session-token");

  return { loggedIn: Boolean(token) };
}
