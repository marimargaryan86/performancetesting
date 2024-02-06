import { describe, expect, it } from "vitest";
import type { Offer } from "~/integration/junction-mobile-api/schemas/offer";
import { getSortOffersFunc } from "~/sorting/offer";
import type { SearchOptionsData } from "../../routes/trip-management/book/select-offer/search-options.svelte";

const foo = {
  groups: [
    {
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
    },
  ],
} as unknown as Offer;

const bar = {
  groups: [
    {
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
    },
  ],
} as unknown as Offer;

const baz = {
  groups: [
    {
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
    },
  ],
} as unknown as Offer;

describe("getSortOffersFunc", () => {
  const earliestArrival = { sortBy: "earliest-arrival" } as SearchOptionsData;
  const latestArrival = { sortBy: "latest-arrival" } as SearchOptionsData;
  const earliestDeparture = { sortBy: "earliest-departure" } as SearchOptionsData;
  const latestDeparture = { sortBy: "latest-departure" } as SearchOptionsData;
  const fastest = { sortBy: "fastest" } as SearchOptionsData;
  const price = { sortBy: "lowest-price" } as SearchOptionsData;
  const invalid = { sortBy: "slowest" } as unknown as SearchOptionsData;

  it("returns correct results for valid sort options", () => {
    const comparedOffersByEarliestArrival = getSortOffersFunc(earliestArrival)(foo, bar);
    expect(comparedOffersByEarliestArrival).toBeLessThan(0);

    const comparedOffersByLatestArrival = getSortOffersFunc(latestArrival)(foo, bar);
    expect(comparedOffersByLatestArrival).toBeGreaterThan(0);

    const comparedOffersByEarliestDeparture = getSortOffersFunc(earliestDeparture)(foo, bar);
    expect(comparedOffersByEarliestDeparture).toBeLessThan(0);

    const comparedOffersByLatestDeparture = getSortOffersFunc(latestDeparture)(foo, bar);
    expect(comparedOffersByLatestDeparture).toBeGreaterThan(0);

    const comparedOffersByFastest = getSortOffersFunc(fastest)(foo, bar);
    expect(comparedOffersByFastest).toBeLessThan(0);

    const comparedOffersByPrice = getSortOffersFunc(price)(foo, bar);
    expect(comparedOffersByPrice).toBeLessThan(0);

    const comparedSamePriceOffersByPrice = getSortOffersFunc(price)(bar, baz);
    expect(comparedSamePriceOffersByPrice).toBeGreaterThan(0);
  });

  it("throws an error with invalid sort options", () => {
    const offerA = { id: "foo" } as Offer;
    const offerB = { id: "bar" } as Offer;
    const invalidSort = getSortOffersFunc(invalid);

    expect(() => invalidSort(offerA, offerB)).toThrowError("Unknown sort parameter");
  });
});
