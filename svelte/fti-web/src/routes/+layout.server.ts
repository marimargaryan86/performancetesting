import type { Locale, LocaleData, TimeFormat } from "$lib/i18n";
import lang from "$lib/i18n/lang";

export function load(event): {
  locale: Locale;
  localeData: LocaleData;
  timeFormat: TimeFormat;
} {
  const { locale } = event.locals;
  const localeData = lang[locale];

  const dateTimeFormat = new Intl.DateTimeFormat(locale, { hour: "numeric" });
  const formattedTime = dateTimeFormat.format(new Date());
  const timeFormat =
    formattedTime.includes("AM") || formattedTime.includes("PM") ? "12hour" : "24hour";

  return {
    locale,
    localeData,
    timeFormat,
  };
}
