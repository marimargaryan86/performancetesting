import { vi } from "vitest";
import localeData from "$lib/i18n/lang/en";
import { writable } from "svelte/store";
import i18next from "i18next";

i18next.init({
  lng: "en-GB",
  resources: {
    "en-GB": {
      translation: localeData,
    },
  },
});
i18next.services.formatter?.add("lowercase", (value: string) => value.toLowerCase());

export const setTranslator = vi.fn();
export const getLocale = vi.fn(() => writable("en-GB"));
export const getTranslator = vi.fn(() =>
  writable((key: string, options?: any) => i18next.t(key, options)),
);
