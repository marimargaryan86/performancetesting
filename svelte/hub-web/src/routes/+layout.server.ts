import { redirect } from "@sveltejs/kit";
import type { User } from "integration/ory/schemas/authentication";
import routeConfig from "routeConfig";
import { cookieStore } from "stores/cookie-store.server";

export function load(event): { user?: User; sessionExpiresAt?: Date } {
  const user = event.locals.user;

  if (!user) {
    return {};
  }

  try {
    return {
      user,
      sessionExpiresAt: event.locals.sessionExpiresAt,
    };
  } catch {
    cookieStore.sessionToken.delete(event);

    throw redirect(303, routeConfig.routes.login.root);
  }
}
