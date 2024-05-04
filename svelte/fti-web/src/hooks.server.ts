import type { Handle, MaybePromise } from "@sveltejs/kit";
import languageData from "$lib/i18n/lang";
import type { Locale } from "$lib/i18n";
import { LOCALE_COOKIE } from "./routes/+layout.svelte";

export function handle({ event, resolve }: Parameters<Handle>[0]): MaybePromise<Response> {
  let locale = event.cookies.get(LOCALE_COOKIE) as Locale | undefined;

  if (!locale || !(locale in languageData)) {
    locale = "en-GB";
    event.cookies.set(LOCALE_COOKIE, locale, {
      path: "/",
      httpOnly: false,
      secure: false,
      maxAge: 31536000,
      sameSite: "lax",
    });
  }

  event.locals.locale = locale;

  return resolve(event);
}
