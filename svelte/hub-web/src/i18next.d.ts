import type { LocaleData } from "~/i18n";

declare module "i18next" {
  interface CustomTypeOptions {
    resources: {
      translation: LocaleData;
    };
  }
}
