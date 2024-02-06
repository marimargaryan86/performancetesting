import type { PriceBreakdown } from "~/integration/common/schemas/price";
import { ensureDefined } from "./array";
import { getMaxDate, getMinDate, getTimeDeltaMs } from "./date-time";
import type { Offer } from "~/integration/junction-mobile-api/schemas/offer";
import { summarizePrices } from "./money";
import type { TripOfferPriceQuote } from "~/integration/junction-mobile-api/schemas/trip-offer-price-quote";
import type { OfferSegmentLeg } from "~/integration/common/schemas/offer-segment-leg";

export function getLowestPrice(offer: Offer): number {
  return Math.min(
    ...offer.groups.flatMap((group) =>
      group.options.flatMap((option) => option.price.total.amount),
    ),
  );
}

export function getMinStopCount(offer: Offer): number {
  return Math.min(...offer.groups.flatMap((group) => group.detailsList.length));
}

export function getMinLegCount(offer: Offer): number {
  return Math.min(
    ...offer.groups.flatMap((group) => group.detailsList.flatMap((details) => details.legs.length)),
  );
}

export function getOfferDurationMs(offer: Offer): number {
  const dates = offer.groups.flatMap((group) =>
    group.detailsList.flatMap((details) =>
      details.legs.flatMap((leg) => [leg.arrivalAt, leg.departureAt]),
    ),
  );
  const departureAt = getMinDate(...dates);
  const arrivalAt = getMaxDate(...dates);

  return getTimeDeltaMs(departureAt, arrivalAt);
}

export function getOfferDurationS(offer: Offer): number {
  return Math.floor(getOfferDurationMs(offer) / 1000);
}

export function getOfferDurationM(offer: Offer): number {
  return Math.floor(getOfferDurationS(offer) / 60);
}

export function getEarliestArrival(offer: Offer): Date {
  const arrivals = offer.groups.flatMap((group) =>
    group.detailsList.flatMap((details) => details.legs.map((leg) => leg.arrivalAt)),
  );

  return getMinDate(...arrivals);
}

export function getEarliestDeparture(offer: Offer): Date {
  const departures = offer.groups.flatMap((group) =>
    group.detailsList.flatMap((details) => details.legs.map((leg) => leg.departureAt)),
  );

  return getMinDate(...departures);
}

export function getVendors(offer: Offer): string[] {
  return Array.from(
    new Set(
      offer.groups.flatMap((group) => group.detailsList.flatMap((details) => details.vendor)),
    ),
  ).filter(ensureDefined);
}

export function getTotalPriceBreakdown(priceQuote: TripOfferPriceQuote): PriceBreakdown[] {
  return priceQuote.options
    .flatMap((option) => option.price.breakdown)
    .filter(ensureDefined)
    .reduce<PriceBreakdown[]>((prev, curr) => {
      const existing = prev.find((pb) => pb.type === curr.type);

      if (existing) {
        return prev.splice(prev.indexOf(existing), 1, {
          ...existing,
          price: summarizePrices(existing.price, curr.price),
        });
      }

      return [...prev, curr];
    }, []);
}

export function getLegsFromPriceQuote(priceQuote: TripOfferPriceQuote): OfferSegmentLeg[] {
  return (
    priceQuote.offer?.groups
      .flatMap((group) => group.detailsList.flatMap((details) => details.legs))
      .sort((a, b) => a.departureAt.getTime() - b.departureAt.getTime()) ?? []
  );
}
