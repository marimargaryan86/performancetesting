/* eslint-disable max-nested-callbacks */
import { describe, expect, it } from "vitest";
import {
  getTotalPriceBreakdown,
  getLegsFromPriceQuote,
  getLegsAndSequencesFromPriceQuote,
  getGroups,
  getOffer,
  getLegExtremes,
  getOfferOptionHash,
} from "../offer";
import type * as MobileSchemas from "~/integration/junction-mobile-api/schemas";
import type * as CommonSchemas from "~/integration/common/schemas";
import type { DeepPartial } from "~/integration/ts-helpers";
import type { TripType } from "$lib/components/pages/trip-management/book/search/trip-search-data";

describe("offer utils", () => {
  describe("getTotalPriceBreakdown", () => {
    it("should return the total price breakdown", () => {
      const priceQuote: DeepPartial<MobileSchemas.TripOfferPriceQuote> = {
        options: [
          {
            price: {
              breakdown: [
                {
                  type: "fare" as CommonSchemas.PriceBreakdownType,
                  price: {
                    amount: 100,
                    currency: "USD",
                  },
                },
                {
                  type: "fare" as CommonSchemas.PriceBreakdownType,
                  price: {
                    amount: 200,
                    currency: "USD",
                  },
                },
              ],
            },
          },
        ],
      };
      const result = getTotalPriceBreakdown(priceQuote as MobileSchemas.TripOfferPriceQuote);
      expect(result).toEqual([
        {
          type: "fare",
          price: {
            amount: 100,
            currency: "USD",
          },
        },
      ]);
    });
  });

  describe("getLegsFromPriceQuote", () => {
    it("should return the legs from the price quote", () => {
      const priceQuote: DeepPartial<MobileSchemas.TripOfferPriceQuote> = {
        offer: {
          groups: [
            {
              detailsList: [
                {
                  legs: [
                    {
                      departureAt: new Date("2022-01-01T00:00:00Z"),
                      arrivalAt: new Date("2022-01-01T01:00:00Z"),
                    },
                  ],
                },
              ],
            },
          ],
        },
      };
      const result = getLegsFromPriceQuote(priceQuote as MobileSchemas.TripOfferPriceQuote);
      expect(result).toEqual([
        {
          departureAt: new Date("2022-01-01T00:00:00Z"),
          arrivalAt: new Date("2022-01-01T01:00:00Z"),
        },
      ]);
    });
  });

  describe("getLegsAndSequencesFromPriceQuote", () => {
    it("should return the legs and sequences from the price quote", () => {
      const priceQuote: DeepPartial<MobileSchemas.TripOfferPriceQuote> = {
        offer: {
          groups: [
            {
              detailsList: [
                {
                  legs: [
                    {
                      departureAt: new Date("2022-01-01T00:00:00Z"),
                      arrivalAt: new Date("2022-01-01T01:00:00Z"),
                    },
                  ],
                  sequences: {
                    trip: 1,
                  },
                },
              ],
            },
          ],
        },
      };
      const result = getLegsAndSequencesFromPriceQuote(
        priceQuote as MobileSchemas.TripOfferPriceQuote,
      );
      expect(result).toEqual([
        [
          {
            departureAt: new Date("2022-01-01T00:00:00Z"),
            arrivalAt: new Date("2022-01-01T01:00:00Z"),
          },
          1,
        ],
      ]);
    });
  });

  describe("getGroups", () => {
    const offers: DeepPartial<MobileSchemas.Offer>[] = [
      {
        groups: [
          {
            id: "group1",
            optionIds: ["option1", "option2"],
          },
          {
            id: "group2",
            optionIds: ["option2", "option2"],
          },
        ],
      },
    ];

    it("should return the groups from the offers of a one-way trip", () => {
      const tripType: TripType = "one-way";
      const outboundOptionId: string = "option1";
      const result = getGroups(offers as MobileSchemas.Offer[], tripType, outboundOptionId);
      expect(result).toEqual([
        {
          id: "group1",
          optionIds: ["option1", "option2"],
        },
      ]);
    });

    it("should return the groups from the offers of a round-trip", () => {
      const tripType: TripType = "round-trip";
      const outboundOptionId: string = "option2";
      const result = getGroups(offers as MobileSchemas.Offer[], tripType, outboundOptionId);
      expect(result).toEqual([
        {
          id: "group2",
          optionIds: ["option2", "option2"],
        },
      ]);
    });
  });

  describe("getOffer", () => {
    const offers: DeepPartial<MobileSchemas.Offer>[] = [
      {
        groups: [
          {
            id: "group1",
            optionIds: ["option1", "option2"],
          },
        ],
      },
    ];

    it("should return the offer for a one-way trip", () => {
      const tripType: TripType = "one-way";
      const outbound: Partial<MobileSchemas.OfferOption> = {
        id: "option1",
      };
      const inbound: Partial<MobileSchemas.OfferOption> = {
        id: "option2",
      };
      const result = getOffer({
        offers: offers as MobileSchemas.Offer[],
        tripType,
        outbound: outbound as MobileSchemas.OfferOption,
        inbound: inbound as MobileSchemas.OfferOption,
      });
      expect(result).toEqual({
        groups: [
          {
            id: "group1",
            optionIds: ["option1", "option2"],
          },
        ],
      });
    });

    it("should return the offer for a round-trip", () => {
      const tripType: TripType = "round-trip";
      const outbound: Partial<MobileSchemas.OfferOption> = {
        id: "option1",
      };
      const inbound: Partial<MobileSchemas.OfferOption> = {
        id: "option2",
      };
      const result = getOffer({
        offers: offers as MobileSchemas.Offer[],
        tripType,
        outbound: outbound as MobileSchemas.OfferOption,
        inbound: inbound as MobileSchemas.OfferOption,
      });
      expect(result).toEqual({
        groups: [
          {
            id: "group1",
            optionIds: ["option1", "option2"],
          },
        ],
      });
    });

    it("should return undefined if outbound is missing for one-way trip", () => {
      const tripType: TripType = "one-way";
      const missingOutbound = getOffer({
        offers: offers as MobileSchemas.Offer[],
        tripType,
        // @ts-expect-error: To test logic that handles this
        undefined,
        // @ts-expect-error: To test logic that handles this
        undefined,
      });
      expect(missingOutbound).toEqual(undefined);
    });

    it("should return undefined if outbound and inbound are missing for round-trip", () => {
      const tripType: TripType = "round-trip";
      const missingOutbound = getOffer({
        offers: offers as MobileSchemas.Offer[],
        tripType,
        // @ts-expect-error: To test logic that handles this
        undefined,
        // @ts-expect-error: To test logic that handles this
        undefined,
      });
      expect(missingOutbound).toEqual(undefined);
    });
  });

  describe("getLegExtremes", () => {
    it("should return the start and end leg", () => {
      const details: DeepPartial<MobileSchemas.TripOfferGroupDetails> = {
        legs: [
          {
            departureAt: new Date("2022-01-01T00:00:00Z"),
            arrivalAt: new Date("2022-01-01T01:00:00Z"),
          },
          {
            departureAt: new Date("2022-01-01T02:00:00Z"),
            arrivalAt: new Date("2022-01-01T03:00:00Z"),
          },
        ],
      };
      const result = getLegExtremes(details as MobileSchemas.TripOfferGroupDetails);
      expect(result).toEqual({
        start: {
          departureAt: new Date("2022-01-01T00:00:00Z"),
          arrivalAt: new Date("2022-01-01T01:00:00Z"),
        },
        end: {
          departureAt: new Date("2022-01-01T02:00:00Z"),
          arrivalAt: new Date("2022-01-01T03:00:00Z"),
        },
      });
    });

    it("should throw an error if there are no legs", () => {
      const details: DeepPartial<MobileSchemas.TripOfferGroupDetails> = {
        legs: [],
      };
      expect(() => getLegExtremes(details as MobileSchemas.TripOfferGroupDetails)).toThrow(
        "Could not get start and end leg",
      );
    });
  });

  describe("getOfferOptionHash", () => {
    it("should return a hash that uniquely identifies an offer option", () => {
      const option: DeepPartial<MobileSchemas.OfferOption> = {
        brandName: "brand1",
        price: {
          total: {
            amount: 100,
            currency: "USD",
          },
        },
        detailsList: [
          {
            details: {
              legs: [
                {
                  departureAt: new Date("2022-01-01T00:00:00Z"),
                  arrivalAt: new Date("2022-01-01T01:00:00Z"),
                },
              ],
            },
          },
        ],
      };
      const result = getOfferOptionHash(option as MobileSchemas.OfferOption);
      expect(result).toBe(
        "eyJicmFuZE5hbWUiOiJicmFuZDEiLCJwcmljZSI6eyJhbW91bnQiOjEwMCwiY3VycmVuY3kiOiJVU0QifSwibGVncyI6W3siZGVwYXJ0dXJlQXQiOiIyMDIyLTAxLTAxVDAwOjAwOjAwLjAwMFoiLCJhcnJpdmFsQXQiOiIyMDIyLTAxLTAxVDAxOjAwOjAwLjAwMFoifV19",
      );
    });
  });
});
