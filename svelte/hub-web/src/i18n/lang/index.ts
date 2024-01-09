import type { Locale, LocaleData } from "i18n";
import en from "./en";
import sv from "./sv";
import es from "./es";

export default {
  "en-GB": en,
  "es-ES": es,
  sv,
} satisfies Record<Locale, LocaleData>;
