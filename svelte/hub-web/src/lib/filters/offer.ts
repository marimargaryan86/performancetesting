import type * as MobileSchemas from "~/integration/junction-mobile-api/schemas";

export type OfferFilterFunc = (item: MobileSchemas.OfferGroup) => boolean;

const directOnly: OfferFilterFunc = (item) => item.detailsList.length === 1;

export function getOfferFilterFunc(direct: boolean): OfferFilterFunc {
  if (direct) {
    return directOnly;
  }

  return () => true;
}
