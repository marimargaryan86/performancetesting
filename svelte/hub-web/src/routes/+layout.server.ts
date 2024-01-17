import type { Locale, LocaleData, TimeFormat } from "i18n";
import lang from "i18n/lang";
import type { User } from "integration/ory/schemas/authentication";

export function load(event): {
  user?: User;
  authenticated: boolean;
  sessionExpiresAt?: Date;
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

  if (!event.locals.session) {
    return { authenticated: false, locale, localeData, timeFormat };
  }

  return {
    user: event.locals.user,
    authenticated: true,
    sessionExpiresAt: event.locals.sessionExpiresAt,
    locale,
    localeData,
    timeFormat,
  };
}
