import {
  getEarliestArrival,
  getEarliestDeparture,
  getOfferDurationS,
  getLowestPrice,
  type SearchOptionsData,
} from "$lib/utils/offer";
import type * as MobileSchemas from "~/integration/junction-mobile-api/schemas";

function getArrivalDelta(a: MobileSchemas.Offer, b: MobileSchemas.Offer): number {
  return getEarliestArrival(a).getTime() - getEarliestArrival(b).getTime();
}

function getDepartureDelta(a: MobileSchemas.Offer, b: MobileSchemas.Offer): number {
  return getEarliestDeparture(a).getTime() - getEarliestDeparture(b).getTime();
}

/**
 * Sorts offers according to the specified filter string. When sorting by
 * price, offers with the same price are further sorted by the earliest
 * departure time.
 *
 * See `svelte/hub-web/src/tests/sorting/offer.test.ts` for more context.
 *
 * @param {SearchOptionsData} options - The search options containing the sort criteria.
 * @returns {(a: MobileSchemas.Offer, b: MobileSchemas.Offer) => number} - A comparator function that can be used in array sort.
 *
 * @throws {Error} Throws an error if an unknown sorting parameter is provided.
 *
 * @example
 * // Example usage
 * const offers = [...]; // Array of Offer objects
 * const sortedOffers = offers.sort(getSortOffersFunc(searchOptions));
 */
export function getSortOffersFunc(
  options: SearchOptionsData,
): (a: MobileSchemas.Offer, b: MobileSchemas.Offer) => number {
  return (a, b) => {
    if (options.sortBy === "earliest-arrival") {
      return getArrivalDelta(a, b);
    } else if (options.sortBy === "latest-arrival") {
      return getArrivalDelta(b, a);
    } else if (options.sortBy === "earliest-departure") {
      return getDepartureDelta(a, b);
    } else if (options.sortBy === "latest-departure") {
      return getDepartureDelta(b, a);
    } else if (options.sortBy === "fastest") {
      return getOfferDurationS(a) - getOfferDurationS(b);
    } else if (options.sortBy === "lowest-price") {
      const priceDiff = getLowestPrice(a) - getLowestPrice(b);

      if (priceDiff === 0) {
        return getDepartureDelta(a, b);
      }

      return priceDiff;
    }

    throw new Error("Unknown sort parameter");
  };
}

export function sortOptions(a: MobileSchemas.OfferOption, b: MobileSchemas.OfferOption): number {
  return a.price.total.amount - b.price.total.amount;
}
