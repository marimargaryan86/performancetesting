import {
  offerModel,
  offerGroupModel,
  tripOfferOptionDetailsModel,
  offerOptionModel,
  tripOfferGroupDetailsModel,
  tripOfferPriceQuoteModel,
  type LegTypeModel,
  type CabinClassModel,
  type TripOfferGroupDetailsSchema,
  type TripOfferGroupDetailsModel,
  type TripOfferOptionDetailsSchema,
  type TripOfferOptionDetailsModel,
  type OfferOptionSchema,
  type OfferOptionModel,
  type OfferGroupSchema,
  type OfferGroupModel,
  type OfferSchema,
  type OfferModel,
  type TripOfferPriceQuoteSchema,
  type TripOfferPriceQuoteModel,
} from "../schemas/offer";
import { ensureDefined } from "utils/array";

export function parseOfferGroupDetailsSchema(
  data: TripOfferGroupDetailsSchema,
  included: { legTypes: LegTypeModel[] },
): TripOfferGroupDetailsModel {
  return {
    ...tripOfferGroupDetailsModel.toModel(data),
    legType: included.legTypes.find((item) => item.id === data.relationships.legType.data.id),
  };
}

export function parseOfferOptionDetailsSchema(
  data: TripOfferOptionDetailsSchema,
  included: { cabinClasses: CabinClassModel[] },
): TripOfferOptionDetailsModel {
  return {
    ...tripOfferOptionDetailsModel.toModel(data),
    cabinClass: included.cabinClasses.find(
      (item) => item.id === data.relationships.cabinClass.data.id,
    ),
  };
}

export function parseOfferOptionSchema(
  data: OfferOptionSchema,
  included: { offerOptionDetails: TripOfferOptionDetailsModel[] },
): OfferOptionModel {
  return {
    ...offerOptionModel.toModel(data),
    details: data.relationships.details.data
      .map((item) => included.offerOptionDetails.find((item2) => item.id === item2.id))
      .filter(ensureDefined),
  };
}

export function parseOfferGroupSchema(
  data: OfferGroupSchema,
  included: {
    offerOptions: OfferOptionModel[];
    offerGroupDetails: TripOfferGroupDetailsModel[];
  },
): OfferGroupModel {
  return {
    ...offerGroupModel.toModel(data),
    options: data.relationships.options.data
      .map((item) => included.offerOptions.find((item2) => item.id === item2.id))
      .filter(ensureDefined),
    details: data.relationships.details.data
      .map((item) => included.offerGroupDetails.find((item2) => item.id === item2.id))
      .filter(ensureDefined),
  };
}

export function parseOfferSchema(
  data: OfferSchema,
  included: { offerGroups: OfferGroupModel[] },
): OfferModel {
  return {
    ...offerModel.toModel(data),
    groups: data.relationships.groups.data
      .map((item) => included.offerGroups.find((item2) => item.id === item2.id))
      .filter(ensureDefined),
  };
}

export function parsePriceQuoteSchema(
  data: TripOfferPriceQuoteSchema,
  included: { offers?: OfferModel[] } = {},
): TripOfferPriceQuoteModel {
  const parsed = tripOfferPriceQuoteModel.toModel(data);
  const offer = included.offers?.find((item) => item.id === data.relationships.offer.data.id);
  const options = Array.from(
    new Set(
      offer?.groups.flatMap((group) =>
        group.options.filter((item) => parsed.optionIds.includes(item.id)),
      ) ?? [],
    ),
  );

  return { ...parsed, offer, options };
}
