import { redirect, type MaybePromise } from "@sveltejs/kit";
import type { UserJwtSchema } from "integration/junction-pay/schemas/user";
import jwt from "jsonwebtoken";
import routeConfig from "routeConfig";

export function handle({ event, resolve }): MaybePromise<Response> {
  const token = event.cookies.get("session-token");
  const user = token ? (jwt.decode(token) as UserJwtSchema) : undefined;

  if (token && user) {
    event.locals = {
      ...event.locals,
      user: {
        data: { email: user.user_info.email, id: user.user_info.id, name: "Unknown" },
        sessionExpiresAt: new Date(user.exp * 1000),
        token,
      },
    };

    if (
      event.url.pathname === routeConfig.login.root &&
      !Array.from(event.url.searchParams.keys()).length
    ) {
      throw redirect(303, routeConfig.home);
    }
  } else if (event.url.pathname !== routeConfig.login.root) {
    throw redirect(303, routeConfig.login.root);
  }

  return resolve(event);
}
