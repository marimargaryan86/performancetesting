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
import { startsWith } from "$lib/utils/common";

// Environment variable check
if (!env.JWT_SECRET) {
  // eslint-disable-next-line no-console
  console.error("Error: JWT_SECRET is not set.");
  process.exit(1);
}

function redirectLoggedInUser(pathname: string): void {
  if (startsWith(pathname, routeConfig.routes.login.root, routeConfig.routes.onboarding.root)) {
    throw redirect(303, routeConfig.root);
  }
}

function redirectLoggedOutUser(pathname: string): void {
  if (
    !startsWith(
      pathname,
      routeConfig.routes.adapters.root,
      routeConfig.routes.login.root,
      routeConfig.routes.onboarding.root,
      routeConfig.routes.integration.routes.ory.root,
    )
  ) {
    throw redirect(303, routeConfig.routes.login.root);
  }
}

function authHandle({ event, resolve }: Parameters<Handle>[0]): MaybePromise<Response> {
  const session = cookieStore.sessionToken.get(event);
  const sessionMeta = cookieStore.sessionMetaToken.get(event);

  if (!session) {
    cookieStore.sessionToken.delete(event);
    cookieStore.sessionMetaToken.delete(event);

    redirectLoggedOutUser(event.url.pathname);

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

  redirectLoggedInUser(event.url.pathname);

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
      sameSite: dev ? "lax" : "none",
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
