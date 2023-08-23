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
  BaggageAllowancesSchema,
  OfferGroupSchema,
  OfferOptionSchema,
  TripOfferSchema,
  OfferSegmentLegSchema,
  TripOfferGroupDetailsSchema,
  TripOfferOptionDetailsSchema,
  TripOfferPriceQuoteSchema,
  LegTypeSchema,
  CabinClassSchema,
  GetOfferPriceQuoteResponseSchema,
} from "../schemas/offer";
import { parsePriceBreakdownSchema, parsePriceSchema } from "./money";
import { parsePointSchema } from "./common";

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

export function parseBaggageAllowanceSchema(data: BaggageAllowancesSchema): BaggageAllowanceModel {
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

export function parsePriceQuoteSchema(
  data: TripOfferPriceQuoteSchema,
  offerGroups?: OfferGroupModel[],
): OfferPriceQuoteModel {
  // eslint-disable-next-line no-console
  console.log(offerGroups);

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

export function parseGetPriceQuoteSchema(
  data: GetOfferPriceQuoteResponseSchema,
): OfferPriceQuoteModel {
  const cabinClasses: CabinClassSchema[] = [];
  const offerOptionDetails: TripOfferOptionDetailsSchema[] = [];
  const offerOptions: OfferOptionSchema[] = [];
  const legTypes: LegTypeSchema[] = [];
  const offerGroupDetails: TripOfferGroupDetailsSchema[] = [];
  const offerGroups: OfferGroupSchema[] = [];

  data.included?.forEach((item) => {
    if (item.type === "cabin-classes") {
      cabinClasses.push(item);
    } else if (item.type === "trip-offer-option-details") {
      offerOptionDetails.push(item);
    } else if (item.type === "offer-options") {
      offerOptions.push(item);
    } else if (item.type === "leg-types") {
      legTypes.push(item);
    } else if (item.type === "trip-offer-group-details") {
      offerGroupDetails.push(item);
    } else {
      offerGroups.push(item);
    }
  });

  const cabinClasses_ = cabinClasses.map(parseCabinClassSchema);
  const offerOptionDetails_ = offerOptionDetails.map((item) =>
    parseOfferOptionDetailsSchema(item, cabinClasses_),
  );
  const offerOptions_ = offerOptions.map((item) =>
    parseOfferOptionSchema(item, offerOptionDetails_),
  );
  const legTypes_ = legTypes.map(parseLegTypeSchema);
  const offerGroupDetails_ = offerGroupDetails.map((item) =>
    parseOfferGroupDetailsSchema(item, legTypes_),
  );
  const offerGroups_ = offerGroups.map((item) =>
    parseOfferGroupSchema(item, offerOptions_, offerGroupDetails_),
  );

  return parsePriceQuoteSchema(data.data, offerGroups_);
}
