import schemaModel, { type Infer } from "utils/schema-model";
import type { JourneySchema } from "./journey";
import {
  cabinClassModel,
  legTypeModel,
  type CabinClassSchema,
  type LegTypeSchema,
  type CabinClassIdentifier,
  type LegTypeIdentifier,
} from "./offer";
import { orderModel, type OrderIdentifier, type OrderSchema, type OrderModel } from "./order";
import { pointModel } from "integration/junction-mobile-api/schemas/common";
import { priceModel } from "integration/junction-mobile-api/schemas/price";
import { z } from "zod";

export const bookingStatusIdentifier = z.object({
  id: z.enum([
    "unspecified",
    "pending",
    "confirmed",
    "rejected",
    "not-ticketed",
    "error",
    "cancelled",
  ]),
  type: z.enum(["booking-statuses"]),
});
export type BookingStatusIdentifier = z.infer<typeof bookingStatusIdentifier>;

export const offerSegmentLegModel = schemaModel.create({
  schema: z.object({
    origin: pointModel.schema,
    destination: pointModel.schema,
    departureAt: z.date({ coerce: true }),
    arrivalAt: z.date({ coerce: true }),
  }),
  model: z.object({
    origin: pointModel.model,
    destination: pointModel.model,
    departureAt: z.date({ coerce: true }),
    arrivalAt: z.date({ coerce: true }),
  }),
  toModel: (data) => ({
    origin: pointModel.toModel(data.origin),
    destination: pointModel.toModel(data.destination),
    departureAt: data.departureAt,
    arrivalAt: data.arrivalAt,
  }),
});

export const routeIdentifierModel = schemaModel.create({
  schema: z.object({
    vendor: z.string(),
    operator: z.string().nullable(),
  }),
  model: z.object({
    vendor: z.string(),
    operator: z.string().optional(),
  }),
  toModel: (data) => ({ vendor: data.vendor, operator: data.operator ?? undefined }),
});

const bookingDetailsRelationships: z.ZodType<{
  booking: { data: BookingIdentifier };
  cabinClass: { data: CabinClassIdentifier };
  legType: { data: LegTypeIdentifier };
}> = z.lazy(() =>
  schemaModel.relationships({
    booking: bookingModel.identifier,
    cabinClass: cabinClassModel.identifier,
    legType: legTypeModel.identifier,
  }),
);

export const bookingDetailsModel = schemaModel.create({
  schema: z.object({
    id: z.string(),
    type: z.enum(["trip-booking-details"]),
    attributes: z.object({
      cabinClassName: z.string(),
      vendor: z.string(),
      operator: z.string().nullable(),
      routeIdentifiers: routeIdentifierModel.schema,
      legs: z.array(offerSegmentLegModel.schema),
    }),
    relationships: bookingDetailsRelationships,
    links: schemaModel.links({ self: true }),
  }),
  model: z.object({
    cabinClass: z.string(),
    vendor: z.string(),
    operator: z.string().optional(),
    routeIdentifiers: routeIdentifierModel.model,
    legs: z.array(offerSegmentLegModel.model),
    legType: legTypeModel.model.optional(),
  }),
  toModel: (data) => ({
    legs: [],
    operator: data.attributes.operator ?? undefined,
    routeIdentifiers: routeIdentifierModel.toModel(data.attributes.routeIdentifiers),
    vendor: data.attributes.vendor,
    cabinClass: data.attributes.cabinClassName,
    legType: undefined,
  }),
});
export type BookingDetailsModel = Infer<typeof bookingDetailsModel>;
export type BookingDetailsSchema = Infer<typeof bookingDetailsModel, "schema">;
export type BookingDetailsIdentifier = Infer<typeof bookingDetailsModel, "identifier">;

const bookingRelationships: z.ZodType<{
  order: { data: OrderIdentifier };
  status: { data: BookingStatusIdentifier };
  details: { data: BookingDetailsIdentifier[] };
}> = z.lazy(() =>
  schemaModel.relationships({
    order: orderModel.identifier,
    status: bookingStatusIdentifier,
    details: z.array(bookingDetailsModel.identifier),
  }),
);

const bookingBase = z.object({
  id: z.string(),
  price: priceModel.model,
  operatorReferences: z.array(z.string()),
  externalReference: z.string().optional(),
  status: bookingStatusIdentifier.shape.id,
});

const bookingExt: z.ZodType<
  z.infer<typeof bookingBase> & {
    order?: OrderModel;
    details?: BookingDetailsModel;
  }
> = z.lazy(() =>
  bookingBase.extend({
    order: orderModel.model.optional(),
    details: bookingDetailsModel.model.optional(),
  }),
);

export const bookingModel = schemaModel.create({
  schema: z.object({
    id: z.string(),
    type: z.enum(["trip-bookings"]),
    attributes: z.object({
      totalPrice: priceModel.schema,
      operatorBookingReferences: z.array(z.string()),
      externalReference: z.string(),
    }),
    relationships: bookingRelationships,
    links: schemaModel.links({ self: true }),
  }),
  model: bookingExt,
  toModel: (data) => ({
    id: data.id,
    externalReference: data.attributes.externalReference.length
      ? data.attributes.externalReference
      : undefined,
    operatorReferences: data.attributes.operatorBookingReferences,
    price: priceModel.toModel(data.attributes.totalPrice),
    status: data.relationships.status.data.id,
    details: undefined,
    order: undefined,
  }),
});
export type BookingModel = Infer<typeof bookingModel>;
export type BookingSchema = Infer<typeof bookingModel, "schema">;
export type BookingIdentifier = Infer<typeof bookingModel, "identifier">;

export type BookingIncludes =
  | OrderSchema
  | JourneySchema
  | BookingDetailsSchema
  | CabinClassSchema
  | LegTypeSchema;
