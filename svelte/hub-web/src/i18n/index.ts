import { getContext, setContext } from "svelte";
import type { Readable, Writable } from "svelte/store";
import type lang from "./lang";
import type en from "./lang/en";

export type Locale = keyof typeof lang;
export type LocaleData = typeof en;

const LOCALE = "locale";
const LOCALE_DATA = "localeData";

export function setLocale(locale: Writable<Locale>): void {
  setContext(LOCALE, locale);
}

export function getLocale(): Writable<Locale> {
  return getContext(LOCALE);
}

export function setLocaleData(data: Readable<LocaleData>): void {
  setContext(LOCALE_DATA, data);
}

export function getLocaleData(): Readable<LocaleData> {
  return getContext(LOCALE_DATA);
}
