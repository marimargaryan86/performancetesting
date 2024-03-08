import type { Handle, MaybePromise } from "@sveltejs/kit";
import languageData from "$lib/i18n/lang";
import type { Locale } from "$lib/i18n";

export function handle({ event, resolve }: Parameters<Handle>[0]): MaybePromise<Response> {
  let locale = event.cookies.get("locale") as Locale | undefined;

  if (!locale || !(locale in languageData)) {
    locale = "en";
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
