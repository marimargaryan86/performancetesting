import type {
  Availability,
  PriceQuoteRequiredPassengerInfoType,
  TripOfferPriceQuoteStatus,
} from "integration/junction-mobile-api/schemas/offer";
import type { PriceBreakdownModel, PriceModel } from "./money";
import type { PointModel } from "models/spatial";

export interface OfferSegmentDetailAmenitiesModel {
  beverage: { availability: Availability };
  entertainment: { availability: Availability };
  food: { availability: Availability };
  power: { availability: Availability };
  wifi: { availability: Availability };
}

export interface CabinClassModel {
  id: string;
  name: string;
}

export interface OfferOptionDetailsModel {
  id: string;
  cabinClass: CabinClassModel;
  cabinClassName: string;
  amenities: OfferSegmentDetailAmenitiesModel;
}

export interface BaggageAllowanceModel {
  isIncluded: boolean;
  applicableTo: {
    dateOfBirthAfter: Date;
    dateOfBirthBefore: Date;
  };
}

export interface OfferGroupOptionModel {
  id: string;
  price: PriceModel;
  priceBreakdown?: PriceBreakdownModel[];
  brandName: string;
  details: OfferOptionDetailsModel[];
  baggageAllowance: BaggageAllowanceModel[];
}

export interface OfferSegmentLegModel {
  origin: PointModel;
  destination: PointModel;
  departureAt: Date;
  arrivalAt: Date;
}

export interface LegTypeModel {
  id: string;
  name: string;
}

export interface RouteIdentifiersModel {
  vendor: string;
  operator?: string;
}

export interface OfferGroupDetailsModel {
  id: string;
  legType: LegTypeModel;
  legs: OfferSegmentLegModel[];
  vendor: string;
  operator?: string;
  routeIdentifiers: RouteIdentifiersModel;
  sequences: {
    trip: number;
    segment: number;
  };
}

export interface OfferGroupModel {
  id: string;
  options: OfferGroupOptionModel[];
  details: OfferGroupDetailsModel[];
}

export interface OfferModel {
  id: string;
  expiresAt: Date;
  groups: OfferGroupModel[];
}

export interface PenaltyModel {
  applicableTo: {
    dateOfBirthAfter: Date;
    dateOfBirthBefore: Date;
  };
  type: "exchange" | "refund";
  changeable?: boolean;
  refundable: boolean;
  conditionsApply?: boolean;
  applicability: "before" | "after";
  price?: PriceModel;
}

export interface RuleModel {
  title: string;
  body: string;
}

export interface OfferPriceQuoteModel {
  id: string;
  expiresAt: Date;
  price?: PriceModel;
  priceBreakdown?: PriceBreakdownModel[];
  penalties: PenaltyModel[];
  required: PriceQuoteRequiredPassengerInfoType[];
  rules: RuleModel[];
  status: TripOfferPriceQuoteStatus;
  offerId: string;
  offer?: OfferModel;
  optionIds: string[];
  options: OfferGroupOptionModel[];
}
