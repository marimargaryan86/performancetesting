import { redirect, type Handle, type MaybePromise } from "@sveltejs/kit";
import routeConfig from "routeConfig";
import * as Sentry from "@sentry/sveltekit";
import { sequence } from "@sveltejs/kit/hooks";
import { env } from "$env/dynamic/private";
import { deleteSession, getSession } from "utils/auth";
import { AUTH_ROOT } from "./routes/integration/auth/auth-service";
import type { SessionExtended } from "integration/ory/schemas";

export function authHandle({ event, resolve }: Parameters<Handle>[0]): MaybePromise<Response> {
  let session: SessionExtended | undefined;

  try {
    session = getSession(event);
  } catch {
    deleteSession(event);

    if (event.url.pathname !== routeConfig.routes.login.root && event.url.pathname !== AUTH_ROOT) {
      throw redirect(303, routeConfig.routes.login.root);
    }
  }

  if (session) {
    event.locals.user = session.user;
    event.locals.sessionExpiresAt = session.expiresAt;
    event.locals.session = { id: session.id, token: session.token };

    if (event.url.pathname === routeConfig.routes.login.root) {
      throw redirect(303, routeConfig.root);
    }
  }

  return resolve(event);
}

Sentry.init({
  dsn: env.PUBLIC_SENTRY_DSN,
  tracesSampleRate: 0.1,
});

export const handleError = Sentry.handleErrorWithSentry();

export const handle = sequence(Sentry.sentryHandle(), authHandle);
