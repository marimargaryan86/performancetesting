import { ensureDefined } from "./array";
import { summarizePrices } from "./money";
import type * as MobileSchemas from "~/integration/junction-mobile-api/schemas";
import type * as CommonSchemas from "~/integration/common/schemas";
import type { TripType } from "$lib/components/pages/trip-management/book/search/trip-search-data";

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

type LegSequenceTuple = [
  CommonSchemas.OfferSegmentLeg,
  MobileSchemas.TripOfferGroupDetails["sequences"]["trip"],
];

export function getLegsAndSequencesFromPriceQuote(
  priceQuote: MobileSchemas.TripOfferPriceQuote,
): LegSequenceTuple[] {
  return (
    priceQuote.offer?.groups
      .flatMap((group) =>
        group.detailsList.flatMap((details) =>
          details.legs.map((leg) => [leg, details.sequences.trip] as LegSequenceTuple),
        ),
      )
      .sort((a, b) => a[0].departureAt.getTime() - b[0].departureAt.getTime()) ?? []
  );
}

export function getGroups(
  offers: MobileSchemas.Offer[],
  tripType: TripType,
  outboundOptionId: string | undefined,
): MobileSchemas.OfferGroup[] {
  let groups: (MobileSchemas.OfferGroup | undefined)[] = [];

  if (tripType === "round-trip" && outboundOptionId) {
    groups = offers
      .filter((offer) => offer.groups.find((group) => group.optionIds.includes(outboundOptionId)))
      .flatMap((offer) => offer.groups[1]);
  } else {
    groups = offers.flatMap((offer) => offer.groups[0]);
  }

  const groupIds = Array.from(new Set(groups.map((group) => group?.id)));

  return groupIds.map((id) => groups.find((group) => group?.id === id)).filter(ensureDefined);
}

export function getOffer({
  offers,
  tripType,
  outbound,
  inbound,
}: {
  offers: MobileSchemas.Offer[];
  tripType: TripType;
  outbound: MobileSchemas.OfferOption | undefined;
  inbound: MobileSchemas.OfferOption | undefined;
}): MobileSchemas.Offer | undefined {
  if (tripType === "round-trip") {
    if (!(outbound && inbound)) {
      return undefined;
    }

    return offers.find(
      (item) =>
        item.groups.some((group) => group.optionIds.includes(outbound.id)) &&
        item.groups.some((group) => group.optionIds.includes(inbound.id)),
    );
  }

  if (!outbound) {
    return undefined;
  }

  return offers.find((item) => item.groups.some((group) => group.optionIds.includes(outbound.id)));
}

export function getLegExtremes(details: MobileSchemas.TripOfferGroupDetails | undefined): {
  start: CommonSchemas.OfferSegmentLeg;
  end: CommonSchemas.OfferSegmentLeg;
} {
  const start = details?.legs[0];
  const end = details?.legs.at(-1);

  if (!(start && end)) {
    throw new Error("Could not get start and end leg");
  }

  return { start, end };
}
