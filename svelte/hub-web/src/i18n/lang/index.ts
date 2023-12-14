import type { LocaleData } from "i18n";
import en from "./en";
import sv from "./sv";
import type languages from "./languages";

export default {
  "en-GB": en,
  "sv-SE": sv,
} satisfies Record<(typeof languages)[number]["locale"], LocaleData>;
