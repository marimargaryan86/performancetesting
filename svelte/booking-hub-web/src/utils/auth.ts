import { error, type RequestEvent } from "@sveltejs/kit";

export function getToken(event: RequestEvent): string {
  const token = event.locals.user?.token;

  if (!token) {
    throw error(401, "Unauthorized");
  }

  return token;
}
