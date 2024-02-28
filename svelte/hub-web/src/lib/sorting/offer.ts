import type * as MobileSchemas from "~/integration/junction-mobile-api/schemas";

export const offerSortOptions = [
  "earliest-departure",
  "earliest-arrival",
  "lowest-price",
  "fastest",
] as const;
export type OfferSortOption = (typeof offerSortOptions)[number];
export type OfferSortFunc = (a: MobileSchemas.OfferGroup, b: MobileSchemas.OfferGroup) => number;

const earliestArrival: OfferSortFunc = (a, b) =>
  (a.detailsList.at(-1)?.legs.at(-1)?.arrivalAt.getTime() ?? 0) -
  (b.detailsList.at(-1)?.legs.at(-1)?.arrivalAt.getTime() ?? 0);

const earliestDeparture: OfferSortFunc = (a, b) =>
  (a.detailsList[0]?.legs[0]?.departureAt.getTime() ?? 0) -
  (b.detailsList[0]?.legs[0]?.departureAt.getTime() ?? 0);

const lowestPrice: OfferSortFunc = (a, b) => {
  const diff = (a.options[0]?.price.total.amount ?? 0) - (b.options[0]?.price.total.amount ?? 0);

  if (diff === 0) {
    return earliestDeparture(a, b);
  }

  return diff;
};

const fastest: OfferSortFunc = (a, b) => {
  const aDuration =
    (a.detailsList.at(-1)?.legs.at(-1)?.arrivalAt.getTime() ?? 0) -
    (a.detailsList[0]?.legs[0]?.departureAt.getTime() ?? 0);
  const bDuration =
    (b.detailsList.at(-1)?.legs.at(-1)?.arrivalAt.getTime() ?? 0) -
    (b.detailsList[0]?.legs[0]?.departureAt.getTime() ?? 0);

  return aDuration - bDuration;
};

export function getOfferSortFunc(sortBy: OfferSortOption): OfferSortFunc {
  if (sortBy === "earliest-arrival") {
    return earliestArrival;
  }

  if (sortBy === "earliest-departure") {
    return earliestDeparture;
  }

  if (sortBy === "lowest-price") {
    return lowestPrice;
  }

  if (sortBy === "fastest") {
    return fastest;
  }

  throw new Error("Unknonw sort parameter");
}
