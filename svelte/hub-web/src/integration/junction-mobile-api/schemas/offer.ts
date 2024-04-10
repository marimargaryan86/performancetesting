import type { GetIncluded, GetOKResponse } from "~/integration/common/types";
import type { Specification } from "./__generated__";
import type { IncludedMapping } from "./included";
import * as CommonSchemas from "~/integration/common/schemas";

export type OfferSegmentDetailAmenity = OfferSegmentDetailAmenitySchema["availability"];

export type OfferSegmentDetailAmenitySchema = OfferSegmentDetailAmenitiesSchema["entertainment"];

export const offerSegmentDetailAmenityParser = {
  toModel: (data: OfferSegmentDetailAmenitySchema): OfferSegmentDetailAmenity => data.availability,
};

export type OfferSegmentDetailAmenities = {
  beverage: OfferSegmentDetailAmenity;
  entertainment: OfferSegmentDetailAmenity;
  food: OfferSegmentDetailAmenity;
  power: OfferSegmentDetailAmenity;
  wifi: OfferSegmentDetailAmenity;
  unlimitedMilage?: OfferSegmentDetailAmenity;
  airConditioner?: OfferSegmentDetailAmenity;
};

export type OfferSegmentDetailAmenitiesSchema =
  TripOfferOptionDetailsSchema["attributes"]["amenities"];

export const offerSegmentDetailAmenitiesParser = {
  toModel: (data: OfferSegmentDetailAmenitiesSchema): OfferSegmentDetailAmenities => ({
    beverage: offerSegmentDetailAmenityParser.toModel(data.beverage),
    entertainment: offerSegmentDetailAmenityParser.toModel(data.entertainment),
    food: offerSegmentDetailAmenityParser.toModel(data.food),
    power: offerSegmentDetailAmenityParser.toModel(data.power),
    wifi: offerSegmentDetailAmenityParser.toModel(data.wifi),
    unlimitedMilage: data.unlimitedMileage
      ? offerSegmentDetailAmenityParser.toModel(data.unlimitedMileage)
      : undefined,
    airConditioner: data.airConditioner
      ? offerSegmentDetailAmenityParser.toModel(data.airConditioner)
      : undefined,
  }),
};

export type TripOfferOptionDetails = {
  id: string;
  cabinClassName: string;
  amenities: OfferSegmentDetailAmenities;
  detailsId: string;
  details?: TripOfferGroupDetails;
  cabinClassId: string;
  cabinClass?: CommonSchemas.CabinClass;
};

export type TripOfferOptionDetailsSchema = GetIncluded<
  GetOKResponse<Specification, "/trip-candidates/searches/{tripCandidateSearchId}/offers">,
  "trip-offer-option-details"
>;

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
  legs: CommonSchemas.OfferSegmentLeg[];
  vendor: string;
  operator?: string;
  routeIdentifiers: CommonSchemas.RouteIdentifiers;
  sequences: {
    trip: number;
    segment: number;
  };
  legTypeId: string;
  legType?: CommonSchemas.LegType;
};

export type TripOfferGroupDetailsSchema = GetIncluded<
  GetOKResponse<Specification, "/trip-candidates/searches/{tripCandidateSearchId}/offers">,
  "trip-offer-group-details"
>;

export const tripOfferGroupDetailsParser = {
  toModel: (
    data: TripOfferGroupDetailsSchema,
    included?: IncludedMapping,
  ): TripOfferGroupDetails => {
    const legTypeId = data.relationships.legType.data.id;

    return {
      id: data.id,
      legs: data.attributes.legs.map(CommonSchemas.offerSegmentLegParser.toModel),
      vendor: data.attributes.vendor,
      operator: data.attributes.operator ?? undefined,
      routeIdentifiers: CommonSchemas.routeIdentifiersParser.toModel(
        data.attributes.routeIdentifiers,
      ),
      sequences: { ...data.attributes.sequences },
      legTypeId,
      legType: included?.legTypes?.find(({ id }) => id === legTypeId),
    };
  },
};

export type ApplicableTo = {
  birthDateAfter?: Date;
  birthDateBefore?: Date;
};

export type ApplicableToSchema = TripOfferOptionPenaltyBaggageAllowanceSchema["applicableTo"];

export const applicableToParser = {
  toModel: (data: ApplicableToSchema): ApplicableTo => ({
    birthDateAfter: data.dateOfBirthAfter ? new Date(data.dateOfBirthAfter) : undefined,
    birthDateBefore: data.dateOfBirthBefore ? new Date(data.dateOfBirthBefore) : undefined,
  }),
};

export type TripOfferOptionPenaltyBaggageAllowance = {
  included: boolean;
  applicableTo: ApplicableTo;
};

export type TripOfferOptionPenaltyBaggageAllowanceSchema =
  OfferOptionSchema["attributes"]["baggageAllowances"][number];

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
    total: CommonSchemas.Price;
    breakdown: CommonSchemas.PriceBreakdown[];
  };
  brandName: string;
  baggageAllowance: TripOfferOptionPenaltyBaggageAllowance[];
  detailsIds: string[];
  detailsList: TripOfferOptionDetails[];
};

export type OfferOptionSchema = GetIncluded<
  GetOKResponse<Specification, "/trip-candidates/searches/{tripCandidateSearchId}/offers">,
  "offer-options"
>;

export const offerOptionParser = {
  toModel: (data: OfferOptionSchema, included?: IncludedMapping): OfferOption => {
    const detailsIds = data.relationships.details.data.map(({ id }) => id);

    return {
      id: data.id,
      price: {
        total: CommonSchemas.priceParser.toModel(data.attributes.price),
        breakdown:
          data.attributes.priceBreakdown
            ?.filter((pb) => pb.breakdownType !== "service-mark-up")
            ?.map(CommonSchemas.priceBreakdownParser.toModel) ?? [],
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

export type OfferGroupSchema = GetIncluded<
  GetOKResponse<Specification, "/trip-candidates/searches/{tripCandidateSearchId}/offers">,
  "offer-groups"
>;

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

export type OfferSchema = GetOKResponse<
  Specification,
  "/trip-candidates/searches/{tripCandidateSearchId}/offers"
>["data"][number];

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
