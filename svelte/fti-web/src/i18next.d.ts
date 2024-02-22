import type { LocaleData } from "$lib/i18n";

declare module "i18next" {
  interface CustomTypeOptions {
    resources: {
      translation: LocaleData;
    };
  }
}
