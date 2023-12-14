import type { Locale, LocaleData } from "i18n";
import lang from "i18n/lang";
import type { User } from "integration/ory/schemas/authentication";

export function load(event): {
  user?: User;
  authenticated: boolean;
  sessionExpiresAt?: Date;
  locale: Locale;
  localeData: LocaleData;
} {
  const { locale } = event.locals;
  const localeData = lang[locale];

  if (!event.locals.session) {
    return { authenticated: false, locale, localeData };
  }

  return {
    user: event.locals.user,
    authenticated: true,
    sessionExpiresAt: event.locals.sessionExpiresAt,
    locale,
    localeData,
  };
}
