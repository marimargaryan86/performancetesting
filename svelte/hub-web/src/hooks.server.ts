import { redirect, type MaybePromise } from "@sveltejs/kit";
import type { UserJwtSchema } from "integration/junction-pay/schemas/user";
import jwtDecode from "jwt-decode";
import routeConfig from "routeConfig";

export function handle({ event, resolve }): MaybePromise<Response> {
  const token = event.cookies.get("session-token");
  const user: UserJwtSchema | undefined = token ? jwtDecode(token) : undefined;

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
      event.url.pathname === routeConfig.login &&
      !Array.from(event.url.searchParams.keys()).length
    ) {
      throw redirect(303, routeConfig.home);
    }
  } else if (event.url.pathname !== routeConfig.login) {
    throw redirect(303, routeConfig.login);
  }

  return resolve(event);
}
