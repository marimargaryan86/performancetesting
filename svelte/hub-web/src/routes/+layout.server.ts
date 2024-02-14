import { env } from "$env/dynamic/private";
import type { Locale, LocaleData, TimeFormat } from "$lib/i18n";
import lang from "$lib/i18n/lang";
import { getAvailableFeatures, type Features } from "$lib/utils/feature-flags";
import type * as OrySchemas from "~/integration/ory/schemas";

export function load(event): {
  user?: OrySchemas.User;
  authenticated: boolean;
  sessionExpiresAt?: Date;
  locale: Locale;
  localeData: LocaleData;
  timeFormat: TimeFormat;
  features: Features;
} {
  const { locale } = event.locals;
  const localeData = lang[locale];

  const dateTimeFormat = new Intl.DateTimeFormat(locale, { hour: "numeric" });
  const formattedTime = dateTimeFormat.format(new Date());
  const timeFormat =
    formattedTime.includes("AM") || formattedTime.includes("PM") ? "12hour" : "24hour";

  const features = getAvailableFeatures(env.ENV_NAME, event.locals.user);

  if (!event.locals.session) {
    return { authenticated: false, locale, localeData, timeFormat, features };
  }

  return {
    user: event.locals.user,
    authenticated: true,
    sessionExpiresAt: event.locals.sessionExpiresAt,
    locale,
    localeData,
    timeFormat,
    features,
  };
}
