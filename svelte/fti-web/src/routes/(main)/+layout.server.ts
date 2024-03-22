import type { Locale, LocaleData } from "$lib/i18n/index.js";
export function load(event): { locale: Locale; localeData: LocaleData } {
  return {
    locale: event.locals.locale,
    localeData: {
      title: "Landing",
      sentences: {
        hello: "Hello",
      },
    },
  };
}
