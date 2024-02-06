import {
  offerSegmentLegParser,
  type OfferSegmentLeg,
  type OfferSegmentLegSchema,
} from "~/integration/common/schemas/offer-segment-leg";
import type { IncludedMapping } from "./included";
import {
  routeIdentifiersParser,
  type RouteIdentifiers,
  type RouteIdentifiersSchema,
} from "~/integration/common/schemas/route-identifier";
import type { LegType, LegTypeSchema } from "~/integration/common/schemas/leg-type";
import {
  priceParser,
  type Price,
  type PriceBreakdown,
  type PriceBreakdownSchema,
  type PriceSchema,
  priceBreakdownParser,
} from "~/integration/common/schemas/price";
import type { CabinClass, CabinClassSchema } from "~/integration/common/schemas/cabin-class";

export type OfferSegmentDetailAmenity = "unspecified" | "unavailable" | "available" | "included";

export type OfferSegmentDetailAmenitySchema = {
  availability: "unspecified" | "unavailable" | "available" | "included";
};

export const offerSegmentDetailAmenityParser = {
  toModel: (data: OfferSegmentDetailAmenitySchema): OfferSegmentDetailAmenity => data.availability,
};

export type OfferSegmentDetailAmenities = {
  beverage: OfferSegmentDetailAmenity;
  entertainment: OfferSegmentDetailAmenity;
  food: OfferSegmentDetailAmenity;
  power: OfferSegmentDetailAmenity;
  wifi: OfferSegmentDetailAmenity;
};

export type OfferSegmentDetailAmenitiesSchema = {
  beverage: OfferSegmentDetailAmenitySchema;
  entertainment: OfferSegmentDetailAmenitySchema;
  food: OfferSegmentDetailAmenitySchema;
  power: OfferSegmentDetailAmenitySchema;
  wifi: OfferSegmentDetailAmenitySchema;
};

export const offerSegmentDetailAmenitiesParser = {
  toModel: (data: OfferSegmentDetailAmenitiesSchema): OfferSegmentDetailAmenities => ({
    beverage: offerSegmentDetailAmenityParser.toModel(data.beverage),
    entertainment: offerSegmentDetailAmenityParser.toModel(data.entertainment),
    food: offerSegmentDetailAmenityParser.toModel(data.food),
    power: offerSegmentDetailAmenityParser.toModel(data.power),
    wifi: offerSegmentDetailAmenityParser.toModel(data.wifi),
  }),
};

export type TripOfferOptionDetails = {
  id: string;
  cabinClassName: string;
  amenities: OfferSegmentDetailAmenities;
  detailsId: string;
  details?: TripOfferGroupDetails;
  cabinClassId: string;
  cabinClass?: CabinClass;
};

export type TripOfferOptionDetailsSchema = {
  id: string;
  type: "trip-offer-option-details";
  attributes: {
    cabinClassName: string;
    amenities: OfferSegmentDetailAmenitiesSchema;
  };
  relationships: {
    details: { data: Pick<TripOfferGroupDetailsSchema, "id" | "type"> };
    cabinClass: { data: Pick<CabinClassSchema, "id" | "type"> };
  };
  links: { self: string };
};

export const tripOfferOptionDetailsParser = {
  toModel: (
    data: TripOfferOptionDetailsSchema,
    included?: IncludedMapping,
  ): TripOfferOptionDetails => {
    const detailsId = data.relationships.details.data.id;
    const cabinClassId = data.relationships.cabinClass.data.id;

    return {
      id: data.id,
      cabinClassName: data.attributes.cabinClassName,
      amenities: offerSegmentDetailAmenitiesParser.toModel(data.attributes.amenities),
      detailsId,
      details: included?.tripOfferGroupDetails?.find(({ id }) => id === detailsId),
      cabinClassId,
      cabinClass: included?.cabinClasses?.find(({ id }) => id === cabinClassId),
    };
  },
};

export type TripOfferGroupDetails = {
  id: string;
  legs: OfferSegmentLeg[];
  vendor: string;
  operator?: string;
  routeIdentifiers: RouteIdentifiers;
  sequences: {
    trip: number;
    segment: number;
  };
  legTypeId: string;
  legType?: LegType;
};

export type TripOfferGroupDetailsSchema = {
  id: string;
  type: "trip-offer-group-details";
  attributes: {
    legs: OfferSegmentLegSchema[];
    vendor: string;
    operator: string | null;
    routeIdentifiers: RouteIdentifiersSchema;
    sequences: {
      trip: number;
      segment: number;
    };
  };
  relationships: {
    legType: { data: Pick<LegTypeSchema, "id" | "type"> };
  };
  links: { self: string };
};

export const tripOfferGroupDetailsParser = {
  toModel: (
    data: TripOfferGroupDetailsSchema,
    included?: IncludedMapping,
  ): TripOfferGroupDetails => {
    const legTypeId = data.relationships.legType.data.id;

    return {
      id: data.id,
      legs: data.attributes.legs.map(offerSegmentLegParser.toModel),
      vendor: data.attributes.vendor,
      operator: data.attributes.operator ?? undefined,
      routeIdentifiers: routeIdentifiersParser.toModel(data.attributes.routeIdentifiers),
      sequences: { ...data.attributes.sequences },
      legTypeId,
      legType: included?.legTypes?.find(({ id }) => id === legTypeId),
    };
  },
};

export type ApplicableTo = {
  birthDateAfter: Date;
  birthDateBefore: Date;
};

export type ApplicableToSchema = {
  dateOfBirthAfter: string;
  dateOfBirthBefore: string;
};

export const applicableToParser = {
  toModel: (data: ApplicableToSchema): ApplicableTo => ({
    birthDateAfter: new Date(data.dateOfBirthAfter),
    birthDateBefore: new Date(data.dateOfBirthBefore),
  }),
};

export type TripOfferOptionPenaltyBaggageAllowance = {
  included: boolean;
  applicableTo: ApplicableTo;
};

export type TripOfferOptionPenaltyBaggageAllowanceSchema = {
  isIncluded: boolean;
  applicableTo: ApplicableToSchema;
};

export const tripOfferOptionPenaltyBaggageAllowanceParser = {
  toModel: (
    data: TripOfferOptionPenaltyBaggageAllowanceSchema,
  ): TripOfferOptionPenaltyBaggageAllowance => ({
    included: data.isIncluded,
    applicableTo: applicableToParser.toModel(data.applicableTo),
  }),
};

export type OfferOption = {
  id: string;
  price: {
    total: Price;
    breakdown: PriceBreakdown[];
  };
  brandName: string;
  baggageAllowance: TripOfferOptionPenaltyBaggageAllowance[];
  detailsIds: string[];
  detailsList: TripOfferOptionDetails[];
};

export type OfferOptionSchema = {
  id: string;
  type: "offer-options";
  attributes: {
    price: PriceSchema;
    priceBreakdown?: PriceBreakdownSchema[];
    brandName: string;
    baggageAllowances: TripOfferOptionPenaltyBaggageAllowanceSchema[];
  };
  relationships: {
    details: { data: Pick<TripOfferOptionDetailsSchema, "id" | "type">[] };
  };
  links: { self: string };
};

export const offerOptionParser = {
  toModel: (data: OfferOptionSchema, included?: IncludedMapping): OfferOption => {
    const detailsIds = data.relationships.details.data.map(({ id }) => id);

    return {
      id: data.id,
      price: {
        total: priceParser.toModel(data.attributes.price),
        breakdown:
          data.attributes.priceBreakdown
            ?.filter((pb) => pb.breakdownType !== "service-mark-up")
            ?.map(priceBreakdownParser.toModel) ?? [],
      },
      brandName: data.attributes.brandName,
      baggageAllowance: data.attributes.baggageAllowances.map(
        tripOfferOptionPenaltyBaggageAllowanceParser.toModel,
      ),
      detailsIds,
      detailsList:
        included?.tripOfferOptionDetails?.filter(({ id }) => detailsIds.includes(id)) ?? [],
    };
  },
};

export type OfferGroup = {
  id: string;
  optionIds: string[];
  options: OfferOption[];
  detailsIds: string[];
  detailsList: TripOfferGroupDetails[];
};

export type OfferGroupSchema = {
  id: string;
  type: "offer-groups";
  attributes: object;
  relationships: {
    options: { data: Pick<OfferOptionSchema, "id" | "type">[] };
    details: { data: Pick<TripOfferGroupDetailsSchema, "id" | "type">[] };
  };
  meta?: {
    providerId?: string;
  };
  links: { self: string };
};

export const offerGroupParser = {
  toModel: (data: OfferGroupSchema, included?: IncludedMapping): OfferGroup => {
    const optionIds = data.relationships.options.data.map(({ id }) => id);
    const detailsIds = data.relationships.details.data.map(({ id }) => id);

    return {
      id: data.id,
      optionIds,
      options: included?.offerOptions?.filter(({ id }) => optionIds.includes(id)) ?? [],
      detailsIds,
      detailsList:
        included?.tripOfferGroupDetails?.filter(({ id }) => detailsIds.includes(id)) ?? [],
    };
  },
};

export type Offer = {
  id: string;
  expiresAt: Date;
  groupIds: string[];
  groups: OfferGroup[];
};

export type OfferSchema = {
  id: string;
  type: "offers";
  attributes: {
    expiresAt: string;
  };
  relationships: {
    groups: { data: Pick<OfferGroupSchema, "id" | "type">[] };
  };
  links: { self: string };
};

export const offerParser = {
  toModel: (data: OfferSchema, included?: IncludedMapping): Offer => {
    const groupIds = data.relationships.groups.data.map(({ id }) => id);

    return {
      id: data.id,
      expiresAt: new Date(data.attributes.expiresAt),
      groupIds,
      groups: included?.groups?.filter(({ id }) => groupIds.includes(id)) ?? [],
    };
  },
};
