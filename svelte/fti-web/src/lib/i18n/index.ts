import { getContext, setContext } from "svelte";
import { writable, type Readable, type Writable, derived } from "svelte/store";
import type en from "./lang/en";
import type languages from "./lang/languages";
import i18next from "i18next";

export type Locale = (typeof languages)[number]["locale"];
export type LocaleData = typeof en;
export type TimeFormat = "12hour" | "24hour";
export type Translator = typeof i18next.t;

const TIME_FORMAT = "timeFormat";

export function setTimeFormat(data: Writable<TimeFormat>): Writable<TimeFormat> {
  return setContext(TIME_FORMAT, data);
}

export function getTimeFormat(): Readable<TimeFormat> {
  return getContext(TIME_FORMAT);
}

const LOCALE = "locale";
const LOCALE_DATA = "locale-data";
const T_FUNC = "t-func";

export function setTranslator(
  locale: Locale,
  localeData: LocaleData,
): {
  locale: Writable<Locale>;
  localeData: Writable<LocaleData>;
  t: Readable<Translator>;
} {
  i18next.init({
    lng: locale,
    resources: {
      [locale]: {
        translation: localeData,
      },
    },
  });
  i18next.services.formatter?.add("lowercase", (value: string) => value.toLowerCase());

  const localeStore = setContext(LOCALE, writable(locale));
  const localeDataStore = setContext(LOCALE_DATA, writable(localeData));
  const tStore = setContext<Readable<Translator>>(
    T_FUNC,
    derived([localeStore, localeDataStore], ([nextLocale, nextLang]) => {
      i18next.addResourceBundle(nextLocale, "translation", nextLang);
      i18next.changeLanguage(nextLocale);
      // @ts-expect-error Mattias is busy and he's the only one who knows whats going on here
      return i18next.t;
    }),
  );

  return {
    locale: localeStore,
    localeData: localeDataStore,
    t: tStore,
  };
}

export function getTranslator(): Readable<Translator> {
  return getContext(T_FUNC);
}

export function getLocale(): Writable<Locale> {
  return getContext(LOCALE);
}
