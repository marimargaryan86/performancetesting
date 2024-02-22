import type { Locale, LocaleData } from "$lib/i18n";
import en from "./en";
import de from "./de";

export default {
  "en-GB": en,
  de,
} satisfies Record<Locale, LocaleData>;
