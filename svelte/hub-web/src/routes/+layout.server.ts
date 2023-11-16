import { redirect } from "@sveltejs/kit";
import type { User } from "integration/ory/schemas";
import routeConfig from "routeConfig";
import { deleteSession } from "utils/auth";

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
    deleteSession(event);

    throw redirect(303, routeConfig.routes.login.root);
  }
}
