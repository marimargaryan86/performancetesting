import { describe, expect, it } from "vitest";
import type * as MobileSchemas from "~/integration/junction-mobile-api/schemas";
import { getOfferSortFunc, type OfferSortOption } from "$lib/sorting/offer";

const foo = {
  options: [{ price: { total: { amount: 100 } } }],
  detailsList: [
    {
      legs: [
        {
          departureAt: new Date("2023-09-25T19:10:00.000Z"),
          arrivalAt: new Date("2023-09-25T20:57:00.000Z"),
        },
      ],
    },
  ],
} as MobileSchemas.OfferGroup;

const bar = {
  options: [{ price: { total: { amount: 200 } } }],
  detailsList: [
    {
      legs: [
        {
          departureAt: new Date("2023-09-26T03:56:00.000Z"),
          arrivalAt: new Date("2023-09-26T06:35:00.000Z"),
        },
      ],
    },
  ],
} as MobileSchemas.OfferGroup;

const baz = {
  options: [{ price: { total: { amount: 200 } } }],
  detailsList: [
    {
      legs: [
        {
          departureAt: new Date("2023-09-26T02:56:00.000Z"),
          arrivalAt: new Date("2023-09-26T05:35:00.000Z"),
        },
      ],
    },
  ],
} as MobileSchemas.OfferGroup;

describe("getOfferSortFunc", () => {
  const earliestArrival: OfferSortOption = "earliest-arrival";
  const earliestDeparture: OfferSortOption = "earliest-departure";
  const fastest: OfferSortOption = "fastest";
  const price: OfferSortOption = "lowest-price";

  it("returns correct results for valid sort options", () => {
    const comparedOffersByEarliestArrival = getOfferSortFunc(earliestArrival)(foo, bar);
    expect(comparedOffersByEarliestArrival).toBeLessThan(0);

    const comparedOffersByEarliestDeparture = getOfferSortFunc(earliestDeparture)(foo, bar);
    expect(comparedOffersByEarliestDeparture).toBeLessThan(0);

    const comparedOffersByFastest = getOfferSortFunc(fastest)(foo, bar);
    expect(comparedOffersByFastest).toBeLessThan(0);

    const comparedOffersByPrice = getOfferSortFunc(price)(foo, bar);
    expect(comparedOffersByPrice).toBeLessThan(0);

    const comparedSamePriceOffersByPrice = getOfferSortFunc(price)(bar, baz);
    expect(comparedSamePriceOffersByPrice).toBeGreaterThan(0);
  });

  it("throws an error with invalid sort options", () => {
    const offerA = { id: "foo" } as MobileSchemas.OfferGroup;
    const offerB = { id: "bar" } as MobileSchemas.OfferGroup;

    expect(() => getOfferSortFunc("invalid" as OfferSortOption)(offerA, offerB)).toThrowError(
      "Unknonw sort parameter",
    );
  });
});
