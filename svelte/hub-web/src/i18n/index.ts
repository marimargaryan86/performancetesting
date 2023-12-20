import { getContext, setContext } from "svelte";
import type { Readable, Writable } from "svelte/store";
import type en from "./lang/en";
import type languages from "./lang/languages";

export type Locale = (typeof languages)[number]["locale"];
export type LocaleData = typeof en;
export type Quantity = "singular" | "plural";
export type WordQuantity = Record<Quantity, string>;
export type ContentElement =
  | { type: "p"; html: string }
  | { type: "h2"; html: string }
  | { type: "ul"; items: string[] };

const LOCALE = "locale";
const LOCALE_DATA = "localeData";

export function setLocale(locale: Writable<Locale>): Writable<Locale> {
  return setContext(LOCALE, locale);
}

export function getLocale(): Writable<Locale> {
  return getContext(LOCALE);
}

export function setLocaleData(data: Writable<LocaleData>): Writable<LocaleData> {
  return setContext(LOCALE_DATA, data);
}

export function getLocaleData(): Readable<LocaleData> {
  return getContext(LOCALE_DATA);
}
