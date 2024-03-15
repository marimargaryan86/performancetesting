import type { Locale, LocaleData } from "$lib/i18n";
import en from "./en";
import es from "./es";

export default {
  "en-GB": en as LocaleData,
  "es-ES": es,
} satisfies Record<Locale, LocaleData>;
