import type {
  BaggageAllowanceModel,
  CabinClassModel,
  OfferGroupModel,
  OfferModel,
  OfferOptionDetailsModel,
  OfferGroupOptionModel as OfferOptionModel,
  OfferGroupDetailsModel,
  LegTypeModel,
  OfferSegmentLegModel,
  OfferPriceQuoteModel,
} from "models/booking/offer";
import type {
  BaggageAllowanceSchema,
  OfferGroupSchema,
  OfferOptionSchema,
  TripOfferSchema,
  OfferSegmentLegSchema,
  TripOfferGroupDetailsSchema,
  TripOfferOptionDetailsSchema,
  TripOfferPriceQuoteSchema,
} from "../schemas/offer";
import {
  parsePriceBreakdownSchema,
  parsePriceSchema,
} from "integration/junction-client-api/parsers/money";
import type {
  CabinClassSchema,
  LegTypeSchema,
} from "integration/junction-client-api/schemas/offer";
import { parsePointSchema } from "integration/junction-client-api/parsers/common";

export function parseLegTypeSchema(data: LegTypeSchema): LegTypeModel {
  return {
    id: data.id,
    name: data.attributes.name,
  };
}

export function parseOfferSegmentLegSchema(data: OfferSegmentLegSchema): OfferSegmentLegModel {
  return {
    arrivalAt: new Date(data.arrivalAt),
    departureAt: new Date(data.departureAt),
    destination: parsePointSchema(data.destination),
    origin: parsePointSchema(data.origin),
  };
}

export function parseOfferGroupDetailsSchema(
  data: TripOfferGroupDetailsSchema,
  legTypes: LegTypeModel[],
): OfferGroupDetailsModel {
  const legType = legTypes.find((item) => item.id === data.relationships.legType.data.id);

  if (!legType) {
    throw new Error("Leg type not found");
  }

  return {
    id: data.id,
    legType,
    legs: data.attributes.legs.map(parseOfferSegmentLegSchema),
    operator: data.attributes.operator ?? undefined,
    vendor: data.attributes.vendor,
    sequences: {
      segment: data.attributes.sequences.segment,
      trip: data.attributes.sequences.trip,
    },
    routeIdentifiers: {
      vendor: data.attributes.routeIdentifiers.vendor,
      operator: data.attributes.routeIdentifiers.operator ?? undefined,
    },
  };
}

export function parseCabinClassSchema(data: CabinClassSchema): CabinClassModel {
  return {
    id: data.id,
    name: data.attributes.name,
  };
}

export function parseOfferOptionDetailsSchema(
  data: TripOfferOptionDetailsSchema,
  cabinClasses: CabinClassModel[],
): OfferOptionDetailsModel {
  const cabinClass = cabinClasses.find((item) => item.id === data.relationships.cabinClass.data.id);

  if (!cabinClass) {
    throw new Error("Cabin class not found");
  }

  return {
    id: data.id,
    cabinClassName: data.attributes.cabinClassName,
    cabinClass,
    amenities: data.attributes.amenities,
  };
}

export function parseBaggageAllowanceSchema(data: BaggageAllowanceSchema): BaggageAllowanceModel {
  return {
    isIncluded: data.isIncluded,
    applicableTo: {
      dateOfBirthBefore: new Date(data.applicableTo.dateOfBirthBefore),
      dateOfBirthAfter: new Date(data.applicableTo.dateOfBirthAfter),
    },
  };
}

export function parseOfferOptionSchema(
  data: OfferOptionSchema,
  offerOptionDetails: OfferOptionDetailsModel[],
): OfferOptionModel {
  return {
    id: data.id,
    price: parsePriceSchema(data.attributes.price),
    priceBreakdown: data.attributes.priceBreakdown?.map(parsePriceBreakdownSchema),
    brandName: data.attributes.brandName,
    details: data.relationships.details.data
      .map((item) => offerOptionDetails.find((item2) => item.id === item2.id))
      .filter((item): item is OfferOptionDetailsModel => Boolean(item)),
    baggageAllowance: data.attributes.baggageAllowances.map((item) =>
      parseBaggageAllowanceSchema(item),
    ),
  };
}

export function parseOfferGroupSchema(
  data: OfferGroupSchema,
  offerOptions: OfferOptionModel[],
  offerGroupDetails: OfferGroupDetailsModel[],
): OfferGroupModel {
  return {
    id: data.id,
    options: data.relationships.options.data
      .map((item) => offerOptions.find((item2) => item.id === item2.id))
      .filter((item): item is OfferOptionModel => Boolean(item)),
    details: data.relationships.details.data
      .map((item) => offerGroupDetails.find((item2) => item.id === item2.id))
      .filter((item): item is OfferGroupDetailsModel => Boolean(item)),
  };
}

export function parseOfferSchema(
  data: TripOfferSchema,
  offerGroups: OfferGroupModel[],
): OfferModel {
  return {
    id: data.id,
    expiresAt: new Date(data.attributes.expiresAt),
    groups: data.relationships.groups.data
      .map((item) => offerGroups.find((item2) => item.id === item2.id))
      .filter((item): item is OfferGroupModel => Boolean(item)),
  };
}

export function parsePriceQuoteSchema(data: TripOfferPriceQuoteSchema): OfferPriceQuoteModel {
  return {
    id: data.id,
    expiresAt: new Date(data.attributes.expiresAt),
    offerId: data.relationships.offer.data.id,
    optionIds: data.relationships.options.data.map((item) => item.id),
    penalties: [],
    priceBreakdown: [],
    required: data.attributes.required,
    rules: [],
    status: data.attributes.status,
    price: data.attributes.price ? parsePriceSchema(data.attributes.price) : undefined,
  };
}
