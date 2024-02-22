import type { Locale, LocaleData } from "$lib/i18n/index.js";
import languageData from "$lib/i18n/lang";

export function load(event): { locale: Locale; localeData: LocaleData } {
  return {
    locale: event.locals.locale,
    localeData: languageData[event.locals.locale],
  };
}
