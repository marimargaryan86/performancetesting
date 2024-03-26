import { redirect, type Handle, type MaybePromise } from "@sveltejs/kit";
import routeConfig from "$lib/route-config";
import * as Sentry from "@sentry/sveltekit";
import { sequence } from "@sveltejs/kit/hooks";
import { env } from "$env/dynamic/private";
import { cookieStore } from "$lib/stores/cookie-store.server";
import type { Locale } from "$lib/i18n";
import languageData from "$lib/i18n/lang";
import { dev } from "$app/environment";
import { LOCALE_COOKIE } from "./routes/+layout.svelte";

// Environment variable check
if (!env.JWT_SECRET) {
  // eslint-disable-next-line no-console
  console.error("Error: JWT_SECRET is not set.");
  process.exit(1);
}

function authHandle({ event, resolve }: Parameters<Handle>[0]): MaybePromise<Response> {
  const session = cookieStore.sessionToken.get(event);
  const sessionMeta = cookieStore.sessionMetaToken.get(event);

  if (!session) {
    cookieStore.sessionToken.delete(event);
    cookieStore.sessionMetaToken.delete(event);

    if (
      !event.url.pathname.startsWith(routeConfig.routes.adapter.root) &&
      !event.url.pathname.startsWith(routeConfig.routes.login.root) &&
      !event.url.pathname.startsWith(routeConfig.routes.integration.routes.ory.root)
    ) {
      // Only allow the login page and the Ory integration for sessionless users.
      throw redirect(303, routeConfig.routes.login.root);
    }

    return resolve(event);
  }

  event.locals.session = session;

  if (!sessionMeta) {
    // Only allow the account settings page and the Ory integration if no session meta is available
    if (
      !event.url.pathname.startsWith(routeConfig.routes.account.root) &&
      !event.url.pathname.startsWith(routeConfig.routes.integration.routes.ory.root)
    ) {
      throw redirect(303, routeConfig.routes.account.root);
    }

    return resolve(event);
  }

  event.locals.user = sessionMeta.user;
  event.locals.sessionExpiresAt = sessionMeta.expiresAt;

  if (event.url.pathname.startsWith(routeConfig.routes.login.root)) {
    // Don't allow logged in users to view the login page
    throw redirect(303, routeConfig.root);
  }

  return resolve(event);
}

/**
 * Sets the default locale as `"en-GB"` if not specifed in the cookie.
 *
 */
function localeHandle({ event, resolve }: Parameters<Handle>[0]): MaybePromise<Response> {
  // Prefix with __Secure if it is secure
  // https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Set-Cookie#cookie_prefixes
  let locale = event.cookies.get(LOCALE_COOKIE) as Locale | undefined;

  if (!locale || !(locale in languageData)) {
    locale = "en-GB";
    event.cookies.set(LOCALE_COOKIE, locale, {
      path: "/",
      httpOnly: false,
      secure: !dev,
      maxAge: 31536000,
      sameSite: dev ? "lax" : "strict",
    });
  }

  event.locals.locale = locale;

  return resolve(event);
}

Sentry.init({
  dsn: env.PUBLIC_SENTRY_DSN,
  tracesSampleRate: 0.1,
});

export const handleError = Sentry.handleErrorWithSentry();

export const handle = sequence(Sentry.sentryHandle(), localeHandle, authHandle);
