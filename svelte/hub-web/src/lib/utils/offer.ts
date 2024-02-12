import { ensureDefined } from "./array";
import { getMaxDate, getMinDate, getTimeDeltaMs } from "./date-time";
import { summarizePrices } from "./money";
import type * as MobileSchemas from "~/integration/junction-mobile-api/schemas";
import type * as CommonSchemas from "~/integration/common/schemas";
import type { Translator } from "$lib/i18n";
import { getFilterOffersFunc } from "$lib/filters/offer";
import { getSortOffersFunc } from "$lib/sorting/offer";

export function getLowestPrice(offer: MobileSchemas.Offer): number {
  return Math.min(
    ...offer.groups.flatMap((group) =>
      group.options.flatMap((option) => option.price.total.amount),
    ),
  );
}

export function getMinStopCount(offer: MobileSchemas.Offer): number {
  return Math.min(...offer.groups.flatMap((group) => group.detailsList.length));
}

export function getMinLegCount(offer: MobileSchemas.Offer): number {
  return Math.min(
    ...offer.groups.flatMap((group) => group.detailsList.flatMap((details) => details.legs.length)),
  );
}

export function getOfferDurationMs(offer: MobileSchemas.Offer): number {
  const dates = offer.groups.flatMap((group) =>
    group.detailsList.flatMap((details) =>
      details.legs.flatMap((leg) => [leg.arrivalAt, leg.departureAt]),
    ),
  );
  const departureAt = getMinDate(...dates);
  const arrivalAt = getMaxDate(...dates);

  return getTimeDeltaMs(departureAt, arrivalAt);
}

export function getOfferDurationS(offer: MobileSchemas.Offer): number {
  return Math.floor(getOfferDurationMs(offer) / 1000);
}

export function getOfferDurationM(offer: MobileSchemas.Offer): number {
  return Math.floor(getOfferDurationS(offer) / 60);
}

export function getEarliestArrival(offer: MobileSchemas.Offer): Date {
  const arrivals = offer.groups.flatMap((group) =>
    group.detailsList.flatMap((details) => details.legs.map((leg) => leg.arrivalAt)),
  );

  return getMinDate(...arrivals);
}

export function getEarliestDeparture(offer: MobileSchemas.Offer): Date {
  const departures = offer.groups.flatMap((group) =>
    group.detailsList.flatMap((details) => details.legs.map((leg) => leg.departureAt)),
  );

  return getMinDate(...departures);
}

export function getVendors(offer: MobileSchemas.Offer): string[] {
  return Array.from(
    new Set(
      offer.groups.flatMap((group) => group.detailsList.flatMap((details) => details.vendor)),
    ),
  ).filter(ensureDefined);
}

export function getTotalPriceBreakdown(
  priceQuote: MobileSchemas.TripOfferPriceQuote,
): CommonSchemas.PriceBreakdown[] {
  return priceQuote.options
    .flatMap((option) => option.price.breakdown)
    .filter(ensureDefined)
    .reduce<CommonSchemas.PriceBreakdown[]>((prev, curr) => {
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

export function getLegsFromPriceQuote(
  priceQuote: MobileSchemas.TripOfferPriceQuote,
): CommonSchemas.OfferSegmentLeg[] {
  return (
    priceQuote.offer?.groups
      .flatMap((group) => group.detailsList.flatMap((details) => details.legs))
      .sort((a, b) => a.departureAt.getTime() - b.departureAt.getTime()) ?? []
  );
}

export const OFFER_SORT_OPTIONS = [
  "lowest-price",
  "fastest",
  "earliest-departure",
  "latest-departure",
  "earliest-arrival",
  "latest-arrival",
] as const;
export type SortOption = (typeof OFFER_SORT_OPTIONS)[number];

export type StopValue = "direct";
export type TimeSpan = { start: number; end: number };

export type SearchOptionsData = {
  sortBy: SortOption;
  stops: StopValue[];
  departureSpanM: TimeSpan;
  arrivalSpanM: TimeSpan;
  durationM: number;
  vendors: string[];
};

export type SearchOptionsSettings = {
  durationSpanM: { start: number; end: number };
  vendors: string[];
};

export function formatTime(minutes: number): string {
  const hours = Math.floor(minutes / 60);
  const minute = minutes % 60;

  return `${hours < 10 ? 0 : ""}${hours}:${minute < 10 ? 0 : ""}${minute}`;
}

export function getFormatSortOptionFunc(translator: Translator): (value?: SortOption) => string {
  return (value) => translator(`sortOptions.${value ? value : "lowest-price"}`);
}

export function getTotalPrice(options: MobileSchemas.OfferOption[]): CommonSchemas.Price {
  return options.reduce<CommonSchemas.Price>(
    (prev, curr) => (prev.amount < curr.price.total.amount ? prev : curr.price.total),
    options[0]?.price.total ?? { amount: 0, currency: "EUR" },
  );
}

export function getCheapestOption(options: MobileSchemas.OfferOption[]): MobileSchemas.OfferOption {
  const initialOption = options[0];

  if (!initialOption) {
    throw new Error("No options available");
  }

  return options.reduce((prev, curr) => {
    return prev.price.total.amount <= curr.price.total.amount ? prev : curr;
  }, initialOption);
}

export function getSortAndFilteringFunc(
  options: SearchOptionsData,
): (offers: MobileSchemas.Offer[]) => MobileSchemas.Offer[] {
  return (offers): MobileSchemas.Offer[] =>
    offers.filter(getFilterOffersFunc(options)).sort(getSortOffersFunc(options));
}

export function getSearchOptionSettings(offers?: MobileSchemas.Offer[]): SearchOptionsSettings {
  if (!offers?.length) {
    return { durationSpanM: { start: 0, end: 0 }, vendors: [] };
  }

  const durations = offers.map((item) => getOfferDurationM(item));
  const vendors = Array.from(new Set(offers.flatMap((item) => getVendors(item))));

  return {
    durationSpanM: {
      start: durations.length ? Math.min(...durations) : 0,
      end: durations.length ? Math.max(...durations) : 0,
    },
    vendors,
  };
}
