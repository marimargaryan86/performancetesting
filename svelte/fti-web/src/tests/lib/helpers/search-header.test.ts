import { describe, expect, it } from "vitest";
import {
  DEFAULT_SEARCH_OPTIONS,
  formatOriginDestination,
  formatDates,
  formatPassengersAndRooms,
} from "$lib/helpers/search-header";

describe("formatOriginDestination", () => {
  it("title cases strings correctly when configured", () => {
    expect(
      formatOriginDestination(
        { ...DEFAULT_SEARCH_OPTIONS, origin: "munich", destination: "bali" },
        { useTitleCase: true },
      ),
    ).toBe("Munich-Bali");
  });

  it("replaces hyphens with spaces correctly when configured", () => {
    expect(
      formatOriginDestination(
        { ...DEFAULT_SEARCH_OPTIONS, origin: "new-york-city", destination: "los-angeles" },
        { replaceHyphensWithSpaces: true, useTitleCase: true },
      ),
    ).toBe("New York City-Los Angeles");
  });

  it("returns destination only when origin is undefined or empty", () => {
    expect(formatOriginDestination({ ...DEFAULT_SEARCH_OPTIONS, destination: "LAX" })).toBe("LAX");

    expect(
      formatOriginDestination({ ...DEFAULT_SEARCH_OPTIONS, origin: "", destination: "SFO" }),
    ).toBe("SFO");
  });

  it("formats non-empty origin and destination", () => {
    expect(
      formatOriginDestination({ ...DEFAULT_SEARCH_OPTIONS, origin: "SFO", destination: "LAX" }),
    ).toBe("SFO-LAX");
  });
});

describe("formatDates", () => {
  it('returns "Anytime" when dates are empty', () => {
    expect(formatDates({ ...DEFAULT_SEARCH_OPTIONS, dates: { start: "", end: "" } })).toBe(
      "Anytime",
    );
  });

  it("formats non-empty dates", () => {
    expect(
      formatDates({
        ...DEFAULT_SEARCH_OPTIONS,
        dates: { start: "08/01/2024", end: "08/15/2024" },
      }),
    ).toBe("08/01/2024-08/15/2024");
  });
});

describe("formatPassengersAndRooms", () => {
  it("formats default passengers and rooms", () => {
    expect(formatPassengersAndRooms(DEFAULT_SEARCH_OPTIONS)).toBe("2 adults, 1 child, 2 rooms");
  });

  it("errors when passengers or rooms is undefined", () => {
    const formatWithErrors = () =>
      formatPassengersAndRooms({ ...DEFAULT_SEARCH_OPTIONS, rooms: undefined });
    expect(formatWithErrors).toThrowError("Rooms undefined.");
  });

  it("formats multiple rooms", () => {
    expect(
      formatPassengersAndRooms({
        ...DEFAULT_SEARCH_OPTIONS,
        passengers: {
          adults: 1,
          children: 2,
        },
        rooms: [
          { adults: 1, children: 0 },
          { adults: 0, children: 2 },
        ],
      }),
    ).toBe("1 adult, 2 children, 2 rooms");
  });

  it("skips children when applicable", () => {
    expect(
      formatPassengersAndRooms({
        ...DEFAULT_SEARCH_OPTIONS,
        passengers: {
          adults: 2,
          children: 0,
        },
        rooms: [
          { adults: 1, children: 0 },
          { adults: 1, children: 0 },
        ],
      }),
    ).toBe("2 adults, 2 rooms");
  });
});
