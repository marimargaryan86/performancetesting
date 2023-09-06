import { priceModel, priceBreakdownModel } from "./price";
import { pointModel, resourceStatus } from "./common";
import { getSchemaModel, links, relationship, type Infer } from "../schema-model.server";
import { z } from "zod";

export const offerSegmentLegModel = getSchemaModel(
  z.object({
    origin: pointModel.schema,
    destination: pointModel.schema,
    departureAt: z.date({ coerce: true }),
    arrivalAt: z.date({ coerce: true }),
  }),
  z.object({
    origin: pointModel.model,
    destination: pointModel.model,
    departureAt: z.date({ coerce: true }),
    arrivalAt: z.date({ coerce: true }),
  }),
  {
    toModel: (data) => ({
      ...data,
      origin: pointModel.toModel(data.origin),
      destination: pointModel.toModel(data.destination),
    }),
    toSchema: (data) => ({
      ...data,
      origin: pointModel.toSchema(data.origin),
      destination: pointModel.toSchema(data.destination),
    }),
  },
);
export type OfferSegmentLegModel = Infer<typeof offerSegmentLegModel>;

export const legTypeModel = getSchemaModel(
  z.object({
    id: z.string(),
    type: z.enum(["leg-types"]),
    attributes: z.object({ name: z.string() }),
    links: links(["self"]),
  }),
  z.object({ id: z.string(), name: z.string() }),
  { toModel: (data) => ({ id: data.id, name: data.attributes.name }) },
);
export type LegTypeModel = Infer<typeof legTypeModel>;
export type LegTypeSchema = Infer<typeof legTypeModel, "schema">;
export type LegTypeIdentifier = Infer<typeof legTypeModel, "identifier">;

export const routeIdentifierModel = getSchemaModel(
  z.object({ vendor: z.string(), operator: z.string().nullable() }),
  z.object({ vendor: z.string(), operator: z.string().optional() }),
  {
    toModel: (data) => ({ ...data, operator: data.operator ?? undefined }),
    toSchema: (data) => ({ ...data, operator: data.operator ?? null }),
  },
);

export const cabinClassModel = getSchemaModel(
  z.object({
    id: z.string(),
    type: z.enum(["cabin-classes"]),
    attributes: z.object({ name: z.string() }),
    links: links(["self"]),
  }),
  z.object({ id: z.string(), name: z.string() }),
  {
    toModel: (data) => ({ id: data.id, name: data.attributes.name }),
  },
);
export type CabinClassModel = Infer<typeof cabinClassModel>;
export type CabinClassSchema = Infer<typeof cabinClassModel, "schema">;
export type CabinClassIdentifier = Infer<typeof cabinClassModel, "identifier">;

export const tripOfferGroupDetailsModel = getSchemaModel(
  z.object({
    id: z.string().uuid(),
    type: z.enum(["trip-offer-group-details"]),
    attributes: z.object({
      legs: z.array(offerSegmentLegModel.schema),
      vendor: z.string(),
      operator: z.string().nullable(),
      routeIdentifiers: routeIdentifierModel.schema,
      sequences: z.object({ trip: z.number(), segment: z.number() }),
    }),
    relationships: relationship({ legType: legTypeModel.schema.pick({ id: true, type: true }) }),
    links: links(["self"]),
  }),
  z.object({
    id: z.string(),
    legType: legTypeModel.model.optional(),
    legs: z.array(offerSegmentLegModel.model),
    vendor: z.string(),
    operator: z.string().optional(),
    routeIdentifiers: routeIdentifierModel.model,
    sequences: z.object({
      trip: z.number(),
      segment: z.number(),
    }),
  }),
  {
    toModel: (data) => ({
      id: data.id,
      legType: undefined,
      legs: data.attributes.legs.map(offerSegmentLegModel.toModel),
      operator: data.attributes.operator ?? undefined,
      vendor: data.attributes.vendor,
      sequences: {
        segment: data.attributes.sequences.segment,
        trip: data.attributes.sequences.trip,
      },
      routeIdentifiers: routeIdentifierModel.toModel(data.attributes.routeIdentifiers),
    }),
  },
);
export type TripOfferGroupDetailsModel = Infer<typeof tripOfferGroupDetailsModel>;
export type TripOfferGroupDetailsSchema = Infer<typeof tripOfferGroupDetailsModel, "schema">;

export const availability = z.enum(["unspecified", "unavailable", "available", "included"]);

export const offerSegmentDetailAmenitiesModel = z.object({
  beverage: z.object({ availability }),
  entertainment: z.object({ availability }),
  food: z.object({ availability }),
  power: z.object({ availability }),
  wifi: z.object({ availability }),
});

export const tripOfferOptionDetailsModel = getSchemaModel(
  z.object({
    id: z.string().uuid(),
    type: z.enum(["trip-offer-option-details"]),
    attributes: z.object({
      cabinClassName: z.string(),
      amenities: offerSegmentDetailAmenitiesModel,
    }),
    relationships: relationship({
      details: tripOfferGroupDetailsModel.schema.pick({ id: true, type: true }),
      cabinClass: cabinClassModel.schema.pick({ id: true, type: true }),
    }),
    links: links(["self"]),
  }),
  z.object({
    id: z.string(),
    cabinClass: cabinClassModel.model.optional(),
    cabinClassName: z.string(),
    amenities: offerSegmentDetailAmenitiesModel,
  }),
  {
    toModel: (data) => ({
      id: data.id,
      cabinClassName: data.attributes.cabinClassName,
      cabinClass: undefined,
      amenities: data.attributes.amenities,
    }),
  },
);
export type TripOfferOptionDetailsModel = Infer<typeof tripOfferOptionDetailsModel>;
export type TripOfferOptionDetailsSchema = Infer<typeof tripOfferOptionDetailsModel, "schema">;

export const baggageAllowanceModel = getSchemaModel(
  z.object({
    isIncluded: z.boolean(),
    applicableTo: z.object({
      dateOfBirthAfter: z.date({ coerce: true }),
      dateOfBirthBefore: z.date({ coerce: true }),
    }),
  }),
  z.object({
    isIncluded: z.boolean(),
    applicableTo: z.object({
      dateOfBirthAfter: z.date({ coerce: true }),
      dateOfBirthBefore: z.date({ coerce: true }),
    }),
  }),
);

export const offerOptionModel = getSchemaModel(
  z.object({
    id: z.string().uuid(),
    type: z.enum(["offer-options"]),
    attributes: z.object({
      price: priceModel.schema,
      priceBreakdown: z.array(priceBreakdownModel.schema).optional(),
      brandName: z.string(),
      baggageAllowances: z.array(baggageAllowanceModel.schema),
    }),
    relationships: relationship({
      details: z.array(tripOfferOptionDetailsModel.schema.pick({ id: true, type: true })),
    }),
    links: links(["self"]),
  }),
  z.object({
    id: z.string(),
    price: priceModel.model,
    priceBreakdown: z.array(priceBreakdownModel.model).optional(),
    brandName: z.string(),
    details: z.array(tripOfferOptionDetailsModel.model),
    baggageAllowance: z.array(baggageAllowanceModel.model),
  }),
  {
    toModel: (data) => ({
      id: data.id,
      price: priceModel.toModel(data.attributes.price),
      priceBreakdown: data.attributes.priceBreakdown?.map(priceBreakdownModel.toModel),
      brandName: data.attributes.brandName,
      details: [],
      baggageAllowance: data.attributes.baggageAllowances.map(baggageAllowanceModel.toModel),
    }),
  },
);
export type OfferOptionModel = Infer<typeof offerOptionModel>;
export type OfferOptionSchema = Infer<typeof offerOptionModel, "schema">;

export const offerGroupModel = getSchemaModel(
  z.object({
    id: z.string().uuid(),
    type: z.enum(["offer-groups"]),
    attributes: z.record(z.any()),
    relationships: relationship({
      options: z.array(offerOptionModel.schema.pick({ id: true, type: true })),
      details: z.array(tripOfferGroupDetailsModel.schema.pick({ id: true, type: true })),
    }),
    links: links(["self"]),
  }),
  z.object({
    id: z.string().uuid(),
    options: z.array(offerOptionModel.model),
    details: z.array(tripOfferGroupDetailsModel.model),
  }),
  { toModel: (data) => ({ id: data.id, options: [], details: [] }) },
);
export type OfferGroupModel = Infer<typeof offerGroupModel>;
export type OfferGroupSchema = Infer<typeof offerGroupModel, "schema">;

export const offerModel = getSchemaModel(
  z.object({
    id: z.string().uuid(),
    type: z.enum(["offers"]),
    attributes: z.object({ expiresAt: z.date({ coerce: true }) }),
    relationships: relationship({
      groups: z.array(offerGroupModel.schema.pick({ id: true, type: true })),
    }),
    links: links(["self"]),
  }),
  z.object({
    id: z.string().uuid(),
    expiresAt: z.date({ coerce: true }),
    groups: z.array(offerGroupModel.model),
  }),
  { toModel: (data) => ({ id: data.id, expiresAt: data.attributes.expiresAt, groups: [] }) },
);
export type OfferModel = Infer<typeof offerModel>;
export type OfferSchema = Infer<typeof offerModel, "schema">;

export const tripOfferOptionPenaltyModel = getSchemaModel(
  z.object({
    applicableTo: z.object({
      dateOfBirthAfter: z.date({ coerce: true }),
      dateOfBirthBefore: z.date({ coerce: true }),
    }),
    penaltyType: z.enum(["exchange", "refund"]),
    changeable: z.boolean().optional(),
    refundable: z.boolean(),
    conditionsApply: z.boolean().optional(),
    applicability: z.enum(["before", "after"]),
    price: priceModel.schema.nullable(),
  }),
  z.object({
    applicableTo: z.object({
      dateOfBirthAfter: z.date({ coerce: true }),
      dateOfBirthBefore: z.date({ coerce: true }),
    }),
    type: z.enum(["exchange", "refund"]),
    changeable: z.boolean().optional(),
    refundable: z.boolean(),
    conditionsApply: z.boolean().optional(),
    applicability: z.enum(["before", "after"]),
    price: priceModel.model.optional(),
  }),
  {
    toModel: (data) => ({
      ...data,
      type: data.penaltyType,
      price: data.price ? priceModel.toModel(data.price) : undefined,
    }),
  },
);

export const offerSegmentDetailRuleModel = z.object({
  title: z.string(),
  body: z.string(),
});

export const priceQuoteRequiredPassengerInfoType = z.enum([
  "date-of-birth",
  "nationality",
  "expiration-date",
  "issuing-country",
  "passport-number",
  "residence-country-code",
  "residence-address",
  "issue-date",
]);

export const tripOfferPriceQuoteModel = getSchemaModel(
  z.object({
    id: z.string().uuid(),
    type: z.enum(["trip-offer-price-quotes"]),
    attributes: z.object({
      expiresAt: z.date({ coerce: true }),
      price: priceModel.schema.nullable(),
      priceBreakdown: z.array(priceBreakdownModel.schema.nullable().optional()),
      penalties: z.array(tripOfferOptionPenaltyModel.schema),
      required: z.array(priceQuoteRequiredPassengerInfoType),
      rules: z.array(offerSegmentDetailRuleModel),
      status: resourceStatus,
    }),
    relationships: relationship({
      offer: offerModel.schema.pick({ id: true, type: true }),
      options: z.array(offerOptionModel.schema.pick({ id: true, type: true })),
    }),
  }),
  z.object({
    id: z.string(),
    expiresAt: z.date({ coerce: true }),
    price: priceModel.model.optional(),
    priceBreakdown: z.array(priceBreakdownModel.model).optional(),
    penalties: z.array(tripOfferOptionPenaltyModel.model),
    required: z.array(priceQuoteRequiredPassengerInfoType),
    rules: z.array(offerSegmentDetailRuleModel),
    status: resourceStatus,
    offerId: z.string(),
    offer: offerModel.model.optional(),
    optionIds: z.array(z.string()),
    options: z.array(offerOptionModel.model),
  }),
  {
    toModel: (data) => ({
      id: data.id,
      expiresAt: data.attributes.expiresAt,
      offerId: data.relationships.offer.data.id,
      offer: undefined,
      optionIds: data.relationships.options.data.map((item) => item.id),
      options: [],
      penalties: data.attributes.penalties.map(tripOfferOptionPenaltyModel.toModel),
      priceBreakdown: data.attributes.priceBreakdown?.map(priceBreakdownModel.toModel),
      required: data.attributes.required,
      rules: data.attributes.rules,
      status: data.attributes.status,
      price: data.attributes.price ? priceModel.toModel(data.attributes.price) : undefined,
    }),
  },
);
export type TripOfferPriceQuoteModel = Infer<typeof tripOfferPriceQuoteModel>;
export type TripOfferPriceQuoteSchema = Infer<typeof tripOfferPriceQuoteModel, "schema">;

export const createTripOfferPriceQuoteModel = getSchemaModel(
  z.object({
    type: z.enum(["trip-offer-price-quotes"]),
    attributes: z.object({ sessionToken: z.string() }).optional(),
    relationships: relationship({
      offer: offerModel.schema.pick({ id: true, type: true }),
      options: z.array(offerOptionModel.schema.pick({ id: true, type: true })),
    }),
  }),
  z.object({
    sessionToken: z.string(),
    offerId: z.string(),
    optionIds: z.array(z.string()),
  }),
  {
    toSchema: (data) => ({
      type: "trip-offer-price-quotes" as const,
      relationships: {
        offer: { data: { id: data.offerId, type: "offers" as const } },
        options: {
          data: data.optionIds.map((id) => ({ id, type: "offer-options" as const })),
        },
      },
    }),
  },
);
export type CreateTripOfferPriceQuoteModel = Infer<typeof createTripOfferPriceQuoteModel>;
export type CreateTripOfferPriceQuoteSchema = Infer<
  typeof createTripOfferPriceQuoteModel,
  "schema"
>;

export type TripOfferPriceQuoteIncludes = (
  | OfferSchema
  | CabinClassSchema
  | TripOfferOptionDetailsSchema
  | OfferOptionSchema
  | LegTypeSchema
  | TripOfferGroupDetailsSchema
  | OfferGroupSchema
)[];

export type OfferIncludes = (
  | OfferGroupSchema
  | TripOfferGroupDetailsSchema
  | LegTypeSchema
  | OfferOptionSchema
  | TripOfferOptionDetailsSchema
  | CabinClassSchema
)[];
