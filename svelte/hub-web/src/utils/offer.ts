import { ensureDefined } from "./array";
import { getMaxDate, getMinDate, getTimeDeltaMs } from "./date-time";
import type { OfferModel } from "integration/junction-mobile-api/schemas/offer";

export function getLowestPrice(offer: OfferModel): number {
  return Math.min(
    ...offer.groups.flatMap((group) => group.options.flatMap((option) => option.price.amount)),
  );
}

export function getMinStopCount(offer: OfferModel): number {
  return Math.min(...offer.groups.flatMap((group) => group.details.length));
}

export function getMinLegCount(offer: OfferModel): number {
  return Math.min(
    ...offer.groups.flatMap((group) => group.details.flatMap((details) => details.legs.length)),
  );
}

export function getOfferDurationMs(offer: OfferModel): number {
  const dates = offer.groups.flatMap((group) =>
    group.details.flatMap((details) =>
      details.legs.flatMap((leg) => [leg.arrivalAt, leg.departureAt]),
    ),
  );
  const departureAt = getMinDate(...dates);
  const arrivalAt = getMaxDate(...dates);

  return getTimeDeltaMs(departureAt, arrivalAt);
}

export function getOfferDurationS(offer: OfferModel): number {
  return Math.floor(getOfferDurationMs(offer) / 1000);
}

export function getOfferDurationM(offer: OfferModel): number {
  return Math.floor(getOfferDurationS(offer) / 60);
}

export function getEarliestArrival(offer: OfferModel): Date {
  const arrivals = offer.groups.flatMap((group) =>
    group.details.flatMap((details) => details.legs.map((leg) => leg.arrivalAt)),
  );

  return getMinDate(...arrivals);
}

export function getEarliestDeparture(offer: OfferModel): Date {
  const departures = offer.groups.flatMap((group) =>
    group.details.flatMap((details) => details.legs.map((leg) => leg.departureAt)),
  );

  return getMinDate(...departures);
}

export function getVendors(offer: OfferModel): string[] {
  return Array.from(
    new Set(offer.groups.flatMap((group) => group.details.flatMap((details) => details.vendor))),
  ).filter(ensureDefined);
}
