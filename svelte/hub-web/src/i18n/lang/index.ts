import type { Locale, LocaleData } from "i18n";
import en from "./en";
import sv from "./sv";

export default {
  "en-GB": en,
  "sv-SE": sv,
} satisfies Record<Locale, LocaleData>;
