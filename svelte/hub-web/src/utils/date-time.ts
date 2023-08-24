export function getZeroTimeDate(date?: Date): Date {
  const nextDate = new Date(date ?? new Date());
  nextDate.setHours(0);
  nextDate.setMinutes(0);
  nextDate.setSeconds(0);
  nextDate.setMilliseconds(0);

  return nextDate;
}

export function getMonths(
  locale = "en-GB",
  options: Intl.DateTimeFormatOptions["month"] = "long",
): Record<number, string> {
  return Object.fromEntries(
    [...Array(12)].map((_, idx) => [
      idx,
      new Date(2023, idx, 1).toLocaleDateString(locale, { month: options }),
    ]),
  ) as Record<number, string>;
}

export function getWeekDays(
  locale = "en-GB",
  options: Intl.DateTimeFormatOptions["weekday"] = "long",
): Record<number, string> {
  const sun = new Date(2023, 0, 1);
  const mon = new Date(2023, 0, 2);
  const tue = new Date(2023, 0, 3);
  const wed = new Date(2023, 0, 4);
  const thu = new Date(2023, 0, 5);
  const fri = new Date(2023, 0, 6);
  const sat = new Date(2023, 0, 7);

  return {
    0: sun.toLocaleDateString(locale, { weekday: options }),
    1: mon.toLocaleDateString(locale, { weekday: options }),
    2: tue.toLocaleDateString(locale, { weekday: options }),
    3: wed.toLocaleDateString(locale, { weekday: options }),
    4: thu.toLocaleDateString(locale, { weekday: options }),
    5: fri.toLocaleDateString(locale, { weekday: options }),
    6: sat.toLocaleDateString(locale, { weekday: options }),
  };
}

export function getMonthLength(date: Date): number {
  return new Date(date.getFullYear(), date.getMonth() + 1, 0).getDate();
}

export function datesEq(date1: Date, date2: Date): boolean {
  return date1.getTime() === date2.getTime();
}

export function getTimeDeltaMs(date1: Date, date2: Date): number {
  return Math.abs(date1.getTime() - date2.getTime());
}

export function getTimeDeltaS(date1: Date, date2: Date): number {
  return Math.floor(getTimeDeltaMs(date1, date2) / 1000);
}
