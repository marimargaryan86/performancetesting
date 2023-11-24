import { redirect, type Handle, type MaybePromise } from "@sveltejs/kit";
import routeConfig from "routeConfig";
import * as Sentry from "@sentry/sveltekit";
import { sequence } from "@sveltejs/kit/hooks";
import { env } from "$env/dynamic/private";
import { ORY_INTEGRATION_ROOT } from "./routes/integration/ory/common";
import { cookieStore } from "stores/cookie-store.server";

export function authHandle({ event, resolve }: Parameters<Handle>[0]): MaybePromise<Response> {
  const session = cookieStore.sessionToken.get(event);
  const sessionMeta = cookieStore.sessionMetaToken.get(event);

  if (session && sessionMeta) {
    event.locals.user = sessionMeta.user;
    event.locals.sessionExpiresAt = sessionMeta.expiresAt;
    event.locals.session = session;

    if (event.url.pathname.startsWith(routeConfig.routes.login.root)) {
      throw redirect(303, routeConfig.root);
    }
  } else {
    cookieStore.sessionToken.delete(event);
    cookieStore.sessionMetaToken.delete(event);

    if (
      !event.url.pathname.startsWith(routeConfig.routes.login.root) &&
      !event.url.pathname.startsWith(ORY_INTEGRATION_ROOT)
    ) {
      throw redirect(303, routeConfig.routes.login.root);
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
