import { redirect, type Handle } from "@sveltejs/kit";
import routeConfig from "routeConfig";
import * as Sentry from "@sentry/sveltekit";
import { sequence } from "@sveltejs/kit/hooks";
import { env } from "$env/dynamic/private";
import { deleteSession, getSession } from "utils/auth";
import integrationInstances from "integration-instances";
import { AUTH_ROOT } from "./routes/integration/auth/auth-service";

export async function authHandle({ event, resolve }: Parameters<Handle>[0]): Promise<Response> {
  try {
    event.locals.user = await integrationInstances.ory.getSession(getSession(event));
  } catch (err) {
    deleteSession(event);

    if (event.url.pathname !== routeConfig.routes.login.root && event.url.pathname !== AUTH_ROOT) {
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
