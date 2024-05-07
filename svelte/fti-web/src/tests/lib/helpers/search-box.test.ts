import { describe, expect, it } from "vitest";
import { constructQueryString } from "$lib/helpers/search-box";
import type { SearchOptions } from "$lib/models/common";

describe("constructQueryString", () => {
  it("should construct a complete query string from search options", () => {
    const searchOptions: SearchOptions = {
      destination: "NYC",
      origin: "LAX",
      searchType: "flights",
      passengers: { adults: 2, children: 1 },
      dates: {
        start: "2021-01-01",
        end: "2021-01-07",
      },
    };
    const queryString = constructQueryString(searchOptions);

    expect(queryString).toContain("destination=NYC");
    expect(queryString).toContain("origin=LAX");
    expect(queryString).toContain("searchType=flights");
    expect(queryString).toContain("passengers.adults=2");
    expect(queryString).toContain("dates.start=2021-01-01");
  });
});
