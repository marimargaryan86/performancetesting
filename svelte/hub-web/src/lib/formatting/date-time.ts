import type { Locale } from "$lib/i18n";
import { ensureDefined } from "$lib/utils/array";

export function formatDuration(
  timeSeconds: number,
  {
    hour = true,
    minute = true,
    second = false,
  }: { hour?: boolean; minute?: boolean; second?: boolean } = {},
): string {
  let hours = 0;
  let minutes = 0;
  let seconds = 0;

  if (hour) {
    hours = Math.floor(timeSeconds / 3600);
  }

  if (minute) {
    minutes = Math.floor((timeSeconds - hours * 3600) / 60);
  }

  if (second) {
    seconds = timeSeconds % 60;
  }

  return [
    hours ? `${hours}h` : undefined,
    minutes ? `${minutes}m` : undefined,
    seconds ? `${seconds}s` : undefined,
  ]
    .filter(ensureDefined)
    .join(" ");
}

export function formatTime(
  time: Date,
  locale: Locale,
  {
    timeZone,
    hour = true,
    minute = true,
    second = false,
  }: {
    timeZone?: string;
    hour?: boolean;
    minute?: boolean;
    second?: boolean;
  } = {},
): string {
  return time.toLocaleTimeString(locale, {
    timeZone,
    minute: minute ? "2-digit" : undefined,
    hour: hour ? "2-digit" : undefined,
    second: second ? "2-digit" : undefined,
  });
}
