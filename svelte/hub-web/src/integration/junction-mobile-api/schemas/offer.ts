import type { RelationshipSchema } from "integration/common/schemas";
import type { PriceBreakdownSchema, PriceSchema } from "./price";
import type { PointSchema } from "./common";

export type Availability = "unspecified" | "unavailable" | "available" | "included";

export interface OfferSegmentDetailAmenitiesSchema {
  beverage: { availability: Availability };
  entertainment: { availability: Availability };
  food: { availability: Availability };
  power: { availability: Availability };
  wifi: { availability: Availability };
}

export interface TripOfferOptionDetailsIdentifierSchema {
  id: string;
  type: "trip-offer-option-details";
}

export interface TripOfferOptionDetailsSchema extends TripOfferOptionDetailsIdentifierSchema {
  attributes: {
    cabinClassName: string;
    amenities: OfferSegmentDetailAmenitiesSchema;
  };
  relationships: {
    details: RelationshipSchema<TripOfferGroupDetailsIdentifierSchema>;
    cabinClass: RelationshipSchema<CabinClassIdentifierSchema>;
  };
  links: { self: string };
}

export interface OfferOptionIdentifierSchema {
  id: string;
  type: "offer-options";
}

export interface BaggageAllowancesSchema {
  isIncluded: boolean;
  applicableTo: {
    dateOfBirthAfter: string;
    dateOfBirthBefore: string;
  };
}

export interface CabinClassIdentifierSchema {
  id: string;
  type: "cabin-classes";
}

export interface CabinClassSchema extends CabinClassIdentifierSchema {
  attributes: {
    name: string;
  };
  links: { self: string };
}

export interface LegTypeIdentifierSchema {
  id: string;
  type: "leg-types";
}

export interface LegTypeSchema extends LegTypeIdentifierSchema {
  attributes: {
    name: string;
  };
  links: { self: string };
}

export interface OfferOptionSchema extends OfferOptionIdentifierSchema {
  attributes: {
    price: PriceSchema;
    priceBreakdown?: PriceBreakdownSchema[];
    brandName: string;
    baggageAllowances: BaggageAllowancesSchema[];
  };
  relationships: {
    details: RelationshipSchema<TripOfferOptionDetailsIdentifierSchema[]>;
  };
  links: { self: string };
}

export interface TripOfferGroupDetailsIdentifierSchema {
  id: string;
  type: "trip-offer-group-details";
}

export interface OfferSegmentLegSchema {
  origin: PointSchema;
  destination: PointSchema;
  departureAt: string;
  arrivalAt: string;
}

export interface RouteIdentifiersSchema {
  vendor: string;
  operator: string | null;
}

export interface TripOfferGroupDetailsSchema extends TripOfferGroupDetailsIdentifierSchema {
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
    legType: RelationshipSchema<LegTypeIdentifierSchema>;
  };
  links: { self: string };
}

export interface OfferGroupIdentifierSchema {
  id: string;
  type: "offer-groups";
}

export interface OfferGroupSchema extends OfferGroupIdentifierSchema {
  attributes: object;
  relationships: {
    options: RelationshipSchema<OfferOptionIdentifierSchema[]>;
    details: RelationshipSchema<TripOfferGroupDetailsIdentifierSchema[]>;
  };
  links: { self: string };
}

export interface TripOfferIdentifierSchema {
  id: string;
  type: "offers";
}

export interface TripOfferSchema extends TripOfferIdentifierSchema {
  attributes: {
    expiresAt: string;
  };
  relationships: {
    groups: RelationshipSchema<OfferGroupIdentifierSchema[]>;
  };
  links: { self: string };
}

export interface TripOfferOptionPenaltySchema {
  applicableTo: {
    dateOfBirthAfter: string;
    dateOfBirthBefore: string;
  };
  penaltyType: "exchange" | "refund";
  changeable?: boolean;
  refundable: boolean;
  conditionsApply?: boolean;
  applicability: "before" | "after";
  price: PriceSchema | null;
}

export interface OfferSegmentDetailRuleSchema {
  title: string;
  body: string;
}

export type TripOfferPriceQuoteStatus =
  | "unspecified"
  | "pending"
  | "processing"
  | "completed"
  | "failed";

export type PriceQuoteRequiredPassengerInfoType =
  | "date-of-birth"
  | "nationality"
  | "expiration-date"
  | "issuing-country"
  | "passport-number"
  | "residence-country-code"
  | "residence-address"
  | "issue-date";

export interface TripOfferPriceQuoteIdentifierSchema {
  id: string;
  type: "trip-offer-price-quotes";
}

export interface TripOfferPriceQuoteSchema extends TripOfferPriceQuoteIdentifierSchema {
  attributes: {
    expiresAt: string;
    price: PriceSchema | null;
    priceBreakdown?: PriceBreakdownSchema[] | null;
    penalties: TripOfferOptionPenaltySchema[];
    required: PriceQuoteRequiredPassengerInfoType[];
    rules: OfferSegmentDetailRuleSchema[];
    status: TripOfferPriceQuoteStatus;
  };
  relationships: {
    offer: RelationshipSchema<TripOfferIdentifierSchema>;
    options: RelationshipSchema<OfferOptionIdentifierSchema[]>;
  };
}

export interface CreateOfferPriceQuoteRequestSchema {
  data: Omit<TripOfferPriceQuoteSchema, "id" | "attributes"> & {
    attributes?: { sessionToken?: string };
  };
}

export interface CreateOfferPriceQuoteResponseSchema {
  data: TripOfferPriceQuoteSchema;
}

export interface GetOfferPriceQuoteResponseSchema {
  data: TripOfferPriceQuoteSchema;
  included?: (
    | TripOfferSchema
    | CabinClassSchema
    | TripOfferOptionDetailsSchema
    | OfferOptionSchema
    | LegTypeSchema
    | TripOfferGroupDetailsSchema
    | OfferGroupSchema
  )[];
}
