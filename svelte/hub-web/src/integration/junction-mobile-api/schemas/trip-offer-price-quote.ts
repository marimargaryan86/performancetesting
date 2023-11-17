import {
  priceParser,
  type Price,
  type PriceBreakdownSchema,
  type PriceSchema,
  type PriceBreakdown,
  priceBreakdownParser,
} from "integration/common/schemas/price";
import {
  applicableToParser,
  type ApplicableTo,
  type ApplicableToSchema,
  type OfferOptionSchema,
  type OfferSchema,
  type Offer,
  type OfferOption,
} from "./offer";
import type { IncludedMapping } from "./included";

export type OfferSegmentDetailRule = {
  title: string;
  body: string;
};

export type OfferSegmentDetailRuleSchema = {
  title: string;
  body: string;
};

export const offerSegmentDetailRuleParser = {
  toModel: (data: OfferSegmentDetailRuleSchema): OfferSegmentDetailRule => ({ ...data }),
};

export type TripOfferOptionPenalty = {
  applicableTo: ApplicableTo;
  penaltyType: "exchange" | "refund";
  changeable?: boolean;
  refundable: boolean;
  conditionsApply?: boolean;
  applicability: "before" | "after";
  price?: Price;
};

export type TripOfferOptionPenaltySchema = {
  applicableTo: ApplicableToSchema;
  penaltyType: "exchange" | "refund";
  changeable?: boolean;
  refundable: boolean;
  conditionsApply?: boolean;
  applicability: "before" | "after";
  price: PriceSchema | null;
};

export const tripOfferOptionPenaltyParser = {
  toModel: (data: TripOfferOptionPenaltySchema): TripOfferOptionPenalty => ({
    applicableTo: applicableToParser.toModel(data.applicableTo),
    penaltyType: data.penaltyType,
    changeable: data.changeable,
    refundable: data.refundable,
    conditionsApply: data.conditionsApply,
    applicability: data.applicability,
    price: data.price ? priceParser.toModel(data.price) : undefined,
  }),
};

type RequiredFields =
  | "date-of-birth"
  | "nationality"
  | "expiration-date"
  | "issuing-country"
  | "passport-number"
  | "residence-country-code"
  | "residence-address"
  | "issue-date";

export type TripOfferPriceQuote = {
  id: string;
  expiresAt: Date;
  price: {
    total?: Price;
    breakdown: PriceBreakdown[];
  };
  penalties: TripOfferOptionPenalty[];
  required: RequiredFields[];
  rules: OfferSegmentDetailRule[];
  status: "unspecified" | "pending" | "processing" | "completed" | "failed";
  offerId: string;
  offer?: Offer;
  optionIds: string[];
  options: OfferOption[];
};

export type TripOfferPriceQuoteSchema = {
  id: string;
  type: "trip-offer-price-quotes";
  attributes: {
    expiresAt: string;
    price: PriceSchema | null;
    priceBreakdown?: PriceBreakdownSchema[] | null;
    penalties: TripOfferOptionPenaltySchema[];
    required: RequiredFields[];
    rules: OfferSegmentDetailRuleSchema[];
    status: "unspecified" | "pending" | "processing" | "completed" | "failed";
  };
  relationships: {
    offer: { data: Pick<OfferSchema, "id" | "type"> };
    options: { data: Pick<OfferOptionSchema, "id" | "type">[] };
  };
  links: { self: string };
};

export type TripOfferPriceQuoteCreate = {
  sessionToken?: string;
  offerId: string;
  optionIds: string[];
};

export type TripOfferPriceQuoteCreateSchema = Pick<
  TripOfferPriceQuoteSchema,
  "type" | "relationships"
> & {
  attributes?: { sessionToken?: string };
};

export const tripOfferPriceQuoteParser = {
  toModel: (data: TripOfferPriceQuoteSchema, included?: IncludedMapping): TripOfferPriceQuote => {
    const offerId = data.relationships.offer.data.id;
    const optionIds = data.relationships.options.data.map(({ id }) => id);

    return {
      id: data.id,
      expiresAt: new Date(data.attributes.expiresAt),
      price: {
        total: data.attributes.price ? priceParser.toModel(data.attributes.price) : undefined,
        breakdown:
          data.attributes.priceBreakdown
            ?.filter((pb) => pb.breakdownType !== "service-mark-up")
            ?.map(priceBreakdownParser.toModel) ?? [],
      },
      penalties: data.attributes.penalties.map(tripOfferOptionPenaltyParser.toModel),
      required: data.attributes.required,
      rules: data.attributes.rules.map(offerSegmentDetailRuleParser.toModel),
      status: data.attributes.status,
      offerId,
      offer: included?.offers?.find(({ id }) => id === offerId),
      optionIds,
      options: included?.offerOptions?.filter(({ id }) => optionIds.includes(id)) ?? [],
    };
  },
  toCreateSchema: (data: TripOfferPriceQuoteCreate): TripOfferPriceQuoteCreateSchema => ({
    type: "trip-offer-price-quotes",
    attributes: data.sessionToken ? { sessionToken: data.sessionToken } : undefined,
    relationships: {
      offer: { data: { id: data.offerId, type: "offers" } },
      options: { data: data.optionIds.map((id) => ({ id, type: "offer-options" })) },
    },
  }),
};
