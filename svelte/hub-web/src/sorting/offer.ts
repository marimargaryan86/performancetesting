import {
  getEarliestArrival,
  getEarliestDeparture,
  getOfferDurationS,
  getLowestPrice,
} from "utils/offer";
import type { SearchOptionsData } from "../routes/trip-management/book/select-offer/search-options.svelte";
import type { OfferModel } from "integration/junction-mobile-api/schemas/offer";

function getArrivalDelta(a: OfferModel, b: OfferModel): number {
  return getEarliestArrival(a).getTime() - getEarliestArrival(b).getTime();
}

function getDepartureDelta(a: OfferModel, b: OfferModel): number {
  return getEarliestDeparture(a).getTime() - getEarliestDeparture(b).getTime();
}

export function getSortOffersFunc(
  options: SearchOptionsData,
): (a: OfferModel, b: OfferModel) => number {
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
    } else if (options.sortBy === "price") {
      return getLowestPrice(a) - getLowestPrice(b);
    }

    throw new Error("Unknown sort parameter");
  };
}
