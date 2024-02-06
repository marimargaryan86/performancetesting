import { describe, expect, it } from "vitest";
import { validateAndGetDate, validateDay, validateMonth, validateYear } from "~/utils/date-time";

describe("validateDay", () => {
  it("should return a valid tuple with a valid day string", () => {
    const result1 = validateDay("01");
    const result2 = validateDay("31");
    const result3 = validateDay("28");

    expect(result1).toEqual([true, null]);
    expect(result2).toEqual([true, null]);
    expect(result3).toEqual([true, null]);
  });

  it("should return an error tuple with an invalid day string", () => {
    const result1 = validateDay("00");
    const result2 = validateDay("141");
    const result3 = validateDay("32");
    const result4 = validateDay("-2");
    const result5 = validateDay("A4");

    expect(result1).toEqual([false, "Invalid day."]);
    expect(result2).toEqual([false, "Invalid day."]);
    expect(result3).toEqual([false, "Invalid day."]);
    expect(result4).toEqual([false, "Invalid day."]);
    expect(result5).toEqual([false, "Invalid day."]);
  });
});

describe("validateMonth", () => {
  it("should return a valid tuple with a valid month string", () => {
    const result1 = validateMonth("01");
    const result2 = validateMonth("12");
    const result3 = validateMonth("09");

    expect(result1).toEqual([true, null]);
    expect(result2).toEqual([true, null]);
    expect(result3).toEqual([true, null]);
  });

  it("should return an error tuple with an invalid month string", () => {
    const result1 = validateMonth("00");
    const result2 = validateMonth("300");
    const result3 = validateMonth("13");
    const result4 = validateMonth("6D");
    const result5 = validateMonth("-1");

    expect(result1).toEqual([false, "Invalid month."]);
    expect(result2).toEqual([false, "Invalid month."]);
    expect(result3).toEqual([false, "Invalid month."]);
    expect(result4).toEqual([false, "Invalid month."]);
    expect(result5).toEqual([false, "Invalid month."]);
  });
});

describe("validateYear", () => {
  it("should return a valid tuple with a valid year string", () => {
    const result1 = validateYear("1900");
    const result2 = validateYear("0000");
    const result3 = validateYear("2023");

    expect(result1).toEqual([true, null]);
    expect(result2).toEqual([true, null]);
    expect(result3).toEqual([true, null]);
  });

  it("should return an error tuple with an invalid year string", () => {
    const result1 = validateYear("42");
    const result2 = validateYear("-1345");
    const result3 = validateYear("year");

    expect(result1).toEqual([false, "Invalid year."]);
    expect(result2).toEqual([false, "Invalid year."]);
    expect(result3).toEqual([false, "Invalid year."]);
  });
});

describe("validateAndGetDate", () => {
  it("should parse a valid date string", () => {
    const validDateString = "22/09/1953";
    const result = validateAndGetDate(validDateString);

    // Month is zero-based, so 8 represents September
    const expectedDate = new Date(1953, 8, 22);

    expect(result).toEqual(expectedDate);
  });

  it("should return undefined for an invalid date string", () => {
    // Invalid format
    const invalidDateString = "09/22/1953";
    const result = validateAndGetDate(invalidDateString);

    expect(result).toBeUndefined();
  });

  it("should return undefined for a non-date string", () => {
    const nonDateString = "fo/oba/rbaz";
    const result = validateAndGetDate(nonDateString);

    expect(result).toBeUndefined();
  });
});
