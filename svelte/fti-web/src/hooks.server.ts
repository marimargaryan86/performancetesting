import type { MaybePromise } from "@sveltejs/kit";
import languageData from "$lib/i18n/lang";
import type { Locale } from "$lib/i18n";

export function handle({ event, resolve }): MaybePromise<Response> {
  let locale = event.cookies.get("locale") as Locale | undefined;

  if (!locale || !(locale in languageData)) {
    locale = "en-GB";
    event.cookies.set("locale", locale, {
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
