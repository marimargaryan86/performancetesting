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

export function datesEq(date1: Date, date2: Date, time = true): boolean {
  if (!time) {
    return getZeroTimeDate(date1).getTime() === getZeroTimeDate(date2).getTime();
  }

  return date1.getTime() === date2.getTime();
}

export function getTimeDeltaMs(date1: Date, date2: Date, absolute = true): number {
  const delta = date1.getTime() - date2.getTime();

  return absolute ? Math.abs(delta) : delta;
}

export function getTimeDeltaS(date1: Date, date2: Date, absolute = true): number {
  return Math.floor(getTimeDeltaMs(date1, date2, absolute) / 1000);
}

export function getMinDate(...dates: Date[]): Date {
  const asTime = dates.map((date) => date.getTime());

  return dates[asTime.indexOf(Math.min(...asTime))] as Date;
}

export function getMaxDate(...dates: Date[]): Date {
  const asTime = dates.map((date) => date.getTime());

  return dates[asTime.indexOf(Math.max(...asTime))] as Date;
}

export function getTimeOfDayMs(date: Date): number {
  return getTimeDeltaMs(date, getZeroTimeDate(date));
}

export function getTimeOfDayS(date: Date): number {
  return Math.round(getTimeOfDayMs(date) / 1000);
}

export function getTimeOfDayM(date: Date): number {
  return Math.fround(getTimeOfDayS(date) / 60);
}

/**
 * Matches a day string and validates that it is a positive two-digit number
 * (including zero-padding) that is between 1 and 31 inclusive. Returns a tuple
 * with a boolean and error string, if any.
 *
 */
export function validateDay(day: string): [isValid: boolean, error: string | null] {
  const regex = /^\d{2}$/;
  let result: [boolean, string | null] = [false, "Invalid day."];

  if (regex.test(day)) {
    const parsedDay = parseInt(day, 10);

    if (parsedDay > 0 && parsedDay <= 31) {
      result = [true, null];
    }
  }

  return result;
}

/**
 * Matches a month string and validates that it is a positive two-digit number
 * (including zero-padding) that is between 1 and 12 inclusive. Returns a tuple
 * with a boolean and error string, if any.
 *
 */
export function validateMonth(month: string): [isValid: boolean, error: string | null] {
  const regex = /^\d{2}$/;
  let result: [boolean, string | null] = [false, "Invalid month."];

  if (regex.test(month)) {
    const parsedMonth = parseInt(month, 10);

    if (parsedMonth > 0 && parsedMonth <= 12) {
      result = [true, null];
    }
  }

  return result;
}

/**
 * Matches a year string and validates that it is a four-digit number
 * (including zero-padding) that is at most the current year. Returns a tuple
 * with a boolean and error string, if any.
 *
 */
export function validateYear(year: string): [isValid: boolean, error: string | null] {
  const regex = /^\d{4}$/;
  let result: [boolean, string | null] = [false, "Invalid year."];

  if (regex.test(year)) {
    const parsedYear = parseInt(year, 10);
    const currentYear: number = new Date().getFullYear();

    if (parsedYear <= currentYear) {
      result = [true, null];
    }
  }

  return result;
}

/**
 * Parses a date string in the format "DD/MM/YYYY" and returns a Date object.
 * Returns `undefined` if in the wrong format or is not a valid date.
 *
 */
export function validateAndGetDate(dateString: string): Date | undefined {
  // Matches strings that represent dates in the format "DD/MM/YYYY" and
  // capture the day, month, and year components into named capture groups.
  const match = dateString.match(/^(?<day>\d{2})\/(?<month>\d{2})\/(?<year>\d{4})$/);

  if (!match?.groups) {
    return undefined;
  }

  const day = match.groups.day as string;
  const month = match.groups.month as string;
  const year = match.groups.year as string;

  const areDatesValid = [validateDay(day)[0], validateMonth(month)[0], validateYear(year)[0]];

  if (areDatesValid.some((isDateValid) => !isDateValid)) {
    return undefined;
  }

  const nextValue = new Date(parseInt(year, 10), parseInt(month, 10) - 1, parseInt(day, 10));

  return isNaN(nextValue.getTime()) ? undefined : nextValue;
}

export function addToDate(
  date: Date,
  options: {
    years?: number;
    months?: number;
    days?: number;
  },
): Date {
  const nextDate = new Date(date);

  if (options.years) {
    nextDate.setFullYear(nextDate.getFullYear() + options.years);
  }

  if (options.months) {
    nextDate.setMonth(nextDate.getMonth() + options.months);
  }

  if (options.days) {
    nextDate.setDate(nextDate.getMonth() + options.days);
  }

  return nextDate;
}
