import type { LocaleData } from "~/i18n";

export function formatStopCount(count: number, locale: LocaleData): string {
  const stops = count - 1;

  if (!stops) {
    return locale.words.direct;
  }

  const stopString = stops === 1 ? locale.words.stop.singular : locale.words.stop.plural;

  return `${stops} ${stopString}`.toLowerCase();
}
