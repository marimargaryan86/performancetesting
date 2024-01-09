import { env } from "$env/dynamic/public";
import * as Sentry from "@sentry/sveltekit";
import Smartlook from "smartlook-client";

Sentry.init({
  dsn: env.PUBLIC_SENTRY_DSN,
  tracesSampleRate: 0.1,
  integrations: [new Sentry.Replay()],
  replaysSessionSampleRate: 0.1,
  replaysOnErrorSampleRate: 1.0,
});

if (env.PUBLIC_SMARTLOOK_PROJECT_KEY) {
  Smartlook.init(env.PUBLIC_SMARTLOOK_PROJECT_KEY);
}

export const handleError = Sentry.handleErrorWithSentry();
