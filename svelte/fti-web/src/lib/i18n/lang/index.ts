import type { Locale, LocaleData } from "$lib/i18n";
import en from "./en";

export default {
  en: en as LocaleData,
} satisfies Record<Locale, LocaleData>;
