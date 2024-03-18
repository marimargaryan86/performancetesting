import { describe, it, expect } from "vitest";
import {
  getZeroTimeDate,
  getTimeDeltaMs,
  getTimeDeltaS,
  getMinDate,
  getMaxDate,
  getTimeOfDayMs,
  getTimeOfDayS,
  getTimeOfDayM,
  validateDay,
  validateMonth,
  validateYear,
  validateAndGetDate,
  getAge,
  parseDateRange,
  getClosestFullHour,
} from "../date-time";

describe("getZeroTimeDate", () => {
  it("should return a date with time set to zero", () => {
    const date1 = new Date(2022, 1, 1, 10, 10, 10, 10);
    const zeroTimeDate1 = getZeroTimeDate(date1);
    expect(zeroTimeDate1.getHours()).toBe(0);
    expect(zeroTimeDate1.getMinutes()).toBe(0);
    expect(zeroTimeDate1.getSeconds()).toBe(0);
    expect(zeroTimeDate1.getMilliseconds()).toBe(0);

    const date2 = new Date(2022, 5, 15, 23, 59, 59, 999);
    const zeroTimeDate2 = getZeroTimeDate(date2);
    expect(zeroTimeDate2.getHours()).toBe(0);
    expect(zeroTimeDate2.getMinutes()).toBe(0);
    expect(zeroTimeDate2.getSeconds()).toBe(0);
    expect(zeroTimeDate2.getMilliseconds()).toBe(0);

    const date3 = new Date(2022, 0, 1, 12, 30, 45, 500);
    const zeroTimeDate3 = getZeroTimeDate(date3);
    expect(zeroTimeDate3.getHours()).toBe(0);
    expect(zeroTimeDate3.getMinutes()).toBe(0);
    expect(zeroTimeDate3.getSeconds()).toBe(0);
    expect(zeroTimeDate3.getMilliseconds()).toBe(0);
  });

  it("should return the current date with time set to zero if no date is provided", () => {
    const currentDate = new Date();
    const zeroTimeDate = getZeroTimeDate();
    expect(zeroTimeDate.getFullYear()).toBe(currentDate.getFullYear());
    expect(zeroTimeDate.getMonth()).toBe(currentDate.getMonth());
    expect(zeroTimeDate.getDate()).toBe(currentDate.getDate());
    expect(zeroTimeDate.getHours()).toBe(0);
    expect(zeroTimeDate.getMinutes()).toBe(0);
    expect(zeroTimeDate.getSeconds()).toBe(0);
    expect(zeroTimeDate.getMilliseconds()).toBe(0);
  });
});

describe("getTimeDeltaMs", () => {
  it("should return the time difference in milliseconds", () => {
    const date1 = new Date(2022, 1, 1, 10, 10, 10, 10);
    const date2 = new Date(2022, 1, 1, 10, 10, 10, 20);
    const delta1 = getTimeDeltaMs(date1, date2);
    expect(delta1).toBe(10);

    const date3 = new Date(2022, 1, 1, 10, 10, 10, 0);
    const date4 = new Date(2022, 1, 1, 10, 10, 11, 0);
    const delta2 = getTimeDeltaMs(date3, date4);
    expect(delta2).toBe(1000);

    const date5 = new Date(2022, 1, 1, 10, 10, 10, 500);
    const date6 = new Date(2022, 1, 1, 10, 10, 11, 200);
    const delta3 = getTimeDeltaMs(date5, date6);
    expect(delta3).toBe(700);

    const date7 = new Date(2022, 1, 1, 10, 10, 10, 999);
    const date8 = new Date(2022, 1, 1, 10, 10, 11, 0);
    const delta4 = getTimeDeltaMs(date7, date8);
    expect(delta4).toBe(1);
  });
});

describe("getTimeDeltaS", () => {
  it("should return the time difference in seconds between dates with no milliseconds", () => {
    const date1 = new Date(2022, 1, 1, 10, 10, 10, 0);
    const date2 = new Date(2022, 1, 1, 10, 10, 20, 0);
    const delta1 = getTimeDeltaS(date1, date2);
    expect(delta1).toBe(10);
  });

  it("should return the time difference in seconds between dates with milliseconds", () => {
    const date1 = new Date(2022, 1, 1, 10, 10, 0, 500);
    const date2 = new Date(2022, 1, 1, 10, 10, 10, 200);
    const delta = getTimeDeltaS(date1, date2);
    expect(delta).toBe(9);
  });

  // TODO(2024-03-05): Investigate if this should be intended behavior or not
  it.skip("should return a negative time difference in seconds", () => {
    const date1 = new Date(2022, 1, 1, 10, 10, 20, 0);
    const date2 = new Date(2022, 1, 1, 10, 10, 10, 0);
    const delta = getTimeDeltaS(date1, date2);
    expect(delta).toBe(-10);
  });

  it("should return 0 when dates are the same", () => {
    const date1 = new Date(2022, 1, 1, 10, 10, 10, 0);
    const date2 = new Date(2022, 1, 1, 10, 10, 10, 0);
    const delta = getTimeDeltaS(date1, date2);
    expect(delta).toBe(0);
  });
});

describe("getMinDate", () => {
  it("should return the earliest date", () => {
    const date1 = new Date(2022, 1, 1);
    const date2 = new Date(2022, 1, 2);
    const date3 = new Date(2022, 1, 3);
    const minDate = getMinDate(date1, date2, date3);
    expect(minDate).toEqual(date1);
  });
});

describe("getMaxDate", () => {
  it("should return the latest date", () => {
    const date1 = new Date(2022, 1, 1);
    const date2 = new Date(2022, 1, 2);
    const date3 = new Date(2022, 1, 3);
    const maxDate = getMaxDate(date1, date2, date3);
    expect(maxDate).toEqual(date3);
  });

  it("should return the latest date when dates are in reverse order", () => {
    const date1 = new Date(2022, 1, 3);
    const date2 = new Date(2022, 1, 2);
    const date3 = new Date(2022, 1, 1);
    const maxDate = getMaxDate(date1, date2, date3);
    expect(maxDate).toEqual(date1);
  });

  it("should return the latest date when dates are the same", () => {
    const date1 = new Date(2022, 1, 1);
    const date2 = new Date(2022, 1, 1);
    const date3 = new Date(2022, 1, 1);
    const maxDate = getMaxDate(date1, date2, date3);
    expect(maxDate).toEqual(date1);
  });

  it("should return the latest date when only one date is provided", () => {
    const date1 = new Date(2022, 1, 1);
    const maxDate = getMaxDate(date1);
    expect(maxDate).toEqual(date1);
  });

  it("should return undefined when no dates are provided", () => {
    const maxDate = getMaxDate();
    expect(maxDate).toBeUndefined();
  });
});

describe("getTimeOfDayMs", () => {
  it("should return the time of day in milliseconds", () => {
    const date = new Date(2022, 1, 1, 10, 10, 10, 10);
    const timeOfDay = getTimeOfDayMs(date);
    expect(timeOfDay).toBe(36610010);
  });
});

describe("getTimeOfDayS", () => {
  it("should return the time of day in seconds", () => {
    const date = new Date(2022, 1, 1, 10, 10, 10, 0);
    const timeOfDay = getTimeOfDayS(date);
    expect(timeOfDay).toBe(36610);
  });
});

describe("getTimeOfDayM", () => {
  it("should return the time of day in minutes", () => {
    const date = new Date(2022, 1, 1, 10, 10, 0, 0);
    const timeOfDay = getTimeOfDayM(date);
    expect(timeOfDay).toBe(610);
  });
});

describe("validateDay", () => {
  it("should return `true` for a valid valid", () => {
    const [isValid] = validateDay("01");
    expect(isValid).toBe(true);
  });

  it("should return `false` for a invalid date", () => {
    const [isValid] = validateDay("32");
    expect(isValid).toBe(false);
  });
});

describe("validateMonth", () => {
  it("should return `true` for a valid month", () => {
    const [isValid] = validateMonth("01");
    expect(isValid).toBe(true);
  });

  it("should return `false` for an invalid month", () => {
    const [isValid] = validateMonth("13");
    expect(isValid).toBe(false);
  });
});

describe("validateYear", () => {
  it("should return `true` for a valid year", () => {
    const [isValid] = validateYear("2022");
    expect(isValid).toBe(true);
  });

  it("should return `false` for an invalid year", () => {
    const [isValid] = validateYear("202");
    expect(isValid).toBe(false);
  });
});

describe("validateAndGetDate", () => {
  it("should validate and get a date when the date is valid", () => {
    const date1 = validateAndGetDate("01/01/2022");
    expect(date1).toEqual(new Date(2022, 0, 1));
  });

  it("should return undefined when the date is invalid", () => {
    const date2 = validateAndGetDate("01/13/2022");
    expect(date2).toBeUndefined();
  });
});

describe("getAge", () => {
  it("should get an age", () => {
    const date = new Date(2000, 1, 1);
    const age = getAge(date);
    expect(age).toBe(new Date().getFullYear() - 2000);
  });
});

describe("parseDateRange", () => {
  it("should parse a valid date range", () => {
    const dateRange = parseDateRange("2022-01-01", "2022-01-02");
    expect(dateRange).toEqual({
      from: getZeroTimeDate(new Date(2022, 0, 1)),
      to: getZeroTimeDate(new Date(2022, 0, 2)),
    });
  });

  it("should return undefined if either date is invalid", () => {
    const dateRange1 = parseDateRange("2022-01-01", "2022-13-02");
    expect(dateRange1).toBeUndefined();

    const dateRange2 = parseDateRange("2022-01-32", "2022-02-01");
    expect(dateRange2).toBeUndefined();
  });

  it("should return undefined if the 'from' date is after the 'to' date", () => {
    const dateRange = parseDateRange("2022-01-02", "2022-01-01");
    expect(dateRange).toBeUndefined();
  });

  it("should return undefined if the date format is incorrect", () => {
    const dateRange2 = parseDateRange("foo", "bar");
    expect(dateRange2).toEqual(undefined);
  });
});

describe("getClosestFullHour", () => {
  it("should get the closest full hour in the future when onlyInFuture is true", () => {
    const now = new Date(Date.UTC(2022, 0, 1, 10, 15, 0));
    const closestFullHour = getClosestFullHour(now, true);
    expect(closestFullHour.getUTCHours()).toBe(11);
    expect(closestFullHour.getUTCMinutes()).toBe(0);
    expect(closestFullHour.getUTCSeconds()).toBe(0);
    expect(closestFullHour.getUTCMilliseconds()).toBe(0);
  });

  it("should get the closest full hour in the past when onlyInFuture is false", () => {
    const now = new Date(Date.UTC(2022, 0, 1, 10, 15, 0));
    const closestFullHour = getClosestFullHour(now, false);
    expect(closestFullHour.getUTCHours()).toBe(10);
    expect(closestFullHour.getUTCMinutes()).toBe(0);
    expect(closestFullHour.getUTCSeconds()).toBe(0);
    expect(closestFullHour.getUTCMilliseconds()).toBe(0);
  });

  it("should get the closest full hour when time is before the half hour mark", () => {
    const now = new Date(Date.UTC(2022, 0, 1, 10, 15, 30));
    const closestFullHour = getClosestFullHour(now, false);
    expect(closestFullHour.getUTCHours()).toBe(10);
    expect(closestFullHour.getUTCMinutes()).toBe(0);
    expect(closestFullHour.getUTCSeconds()).toBe(0);
    expect(closestFullHour.getUTCMilliseconds()).toBe(0);
  });

  it("should get the closest full hour when time is after the half hour mark", () => {
    const now = new Date(Date.UTC(2022, 0, 1, 10, 45, 30));
    const closestFullHour = getClosestFullHour(now, false);
    expect(closestFullHour.getUTCHours()).toBe(11);
    expect(closestFullHour.getUTCMinutes()).toBe(0);
    expect(closestFullHour.getUTCSeconds()).toBe(0);
    expect(closestFullHour.getUTCMilliseconds()).toBe(0);
  });

  it("should get the closest full hour when time is exactly at the half hour mark", () => {
    const now = new Date(Date.UTC(2022, 0, 1, 10, 30, 0));
    const closestFullHour = getClosestFullHour(now, false);
    expect(closestFullHour.getUTCHours()).toBe(11);
    expect(closestFullHour.getUTCMinutes()).toBe(0);
    expect(closestFullHour.getUTCSeconds()).toBe(0);
    expect(closestFullHour.getUTCMilliseconds()).toBe(0);
  });
});
