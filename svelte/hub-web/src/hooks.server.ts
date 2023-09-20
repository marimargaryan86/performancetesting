import { redirect, type MaybePromise, type Handle } from "@sveltejs/kit";
import { userJwtModel } from "integration/junction-pay/schemas/user";
import jwt from "jsonwebtoken";
import routeConfig from "routeConfig";
import * as Sentry from "@sentry/sveltekit";
import { sequence } from "@sveltejs/kit/hooks";
import { env } from "$env/dynamic/public";

export function authHandle({ event, resolve }: Parameters<Handle>[0]): MaybePromise<Response> {
  const token = event.cookies.get("session-token");
  const user = token ? userJwtModel.toModel(jwt.decode(token)) : undefined;

  if (token && user) {
    event.locals = {
      ...event.locals,
      user: {
        data: { email: user.email, id: user.id, name: "Unknown" },
        sessionExpiresAt: user.expiresAt,
        token,
      },
    };

    if (
      event.url.pathname === routeConfig.routes.login.root &&
      !Array.from(event.url.searchParams.keys()).length
    ) {
      throw redirect(303, routeConfig.root);
    }
  } else if (event.url.pathname !== routeConfig.routes.login.root) {
    throw redirect(303, routeConfig.routes.login.root);
  }

  return resolve(event);
}

Sentry.init({
  dsn: env.PUBLIC_SENTRY_DSN,
  tracesSampleRate: 0.1,
});

export const handleError = Sentry.handleErrorWithSentry();

export const handle = sequence(Sentry.sentryHandle(), authHandle);
