import type { User } from "integration/ory/schemas/authentication";

export function load(event): { user?: User; authenticated: boolean; sessionExpiresAt?: Date } {
  if (!event.locals.session) {
    return { authenticated: false };
  }

  return {
    user: event.locals.user,
    authenticated: true,
    sessionExpiresAt: event.locals.sessionExpiresAt,
  };
}
