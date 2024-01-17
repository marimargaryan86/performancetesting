import { getContext, setContext } from "svelte";
import type { Readable, Writable } from "svelte/store";
import type en from "./lang/en";
import type languages from "./lang/languages";

export type Locale = (typeof languages)[number]["locale"];
export type LocaleData = typeof en;
export type TimeFormat = "12hour" | "24hour";
export type Quantity = "singular" | "plural";
export type WordQuantity = Record<Quantity, string>;
export type ContentElement =
  | { type: "p"; html: string }
  | { type: "h2"; html: string }
  | { type: "ul"; items: string[] };

const LOCALE = "locale";
const LOCALE_DATA = "localeData";
const TIME_FORMAT = "timeFormat";

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

export function setTimeFormat(data: Writable<TimeFormat>): Writable<TimeFormat> {
  return setContext(TIME_FORMAT, data);
}

export function getTimeFormat(): Readable<TimeFormat> {
  return getContext(TIME_FORMAT);
}
