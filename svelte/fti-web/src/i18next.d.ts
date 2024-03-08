import type { LocaleData } from "$lib/i18n/lang";

declare module "i18next" {
  interface CustomTypeOptions {
    resources: {
      translation: LocaleData;
    };
  }
}
