import type { JourneySchema } from "./journey";
import { cabinClassModel, legTypeModel, type CabinClassSchema, type LegTypeSchema } from "./offer";
import { orderModel, type OrderSchema } from "./order";
import { pointModel } from "integration/junction-mobile-api/schemas/common";
import { priceModel } from "integration/junction-mobile-api/schemas/price";
import {
  getSchemaModel,
  links,
  relationship,
  type Infer,
} from "integration/common/schema-model.server";
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
      origin: pointModel.toModel(data.origin),
      destination: pointModel.toModel(data.destination),
      departureAt: data.departureAt,
      arrivalAt: data.arrivalAt,
    }),
  },
);

export const routeIdentifierModel = getSchemaModel(
  z.object({
    vendor: z.string(),
    operator: z.string().nullable(),
  }),
  z.object({
    vendor: z.string(),
    operator: z.string().optional(),
  }),
  { toModel: (data) => ({ vendor: data.vendor, operator: data.operator ?? undefined }) },
);

const bookingDetailsRelationships: z.ZodType<{
  booking: { data: Infer<typeof bookingModel, "identifier"> };
  cabinClass: { data: Infer<typeof cabinClassModel, "identifier"> };
  legType: { data: Infer<typeof legTypeModel, "identifier"> };
}> = relationship({
  booking: z.lazy(() => bookingModel.identifier),
  cabinClass: cabinClassModel.identifier,
  legType: legTypeModel.identifier,
});

export const bookingDetailsModel = getSchemaModel(
  z.object({
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
    links: links(["self"]),
  }),
  z.object({
    cabinClass: z.string(),
    vendor: z.string(),
    operator: z.string().optional(),
    routeIdentifiers: routeIdentifierModel.model,
    legs: z.array(offerSegmentLegModel.model),
    legType: legTypeModel.model.optional(),
  }),
  {
    toModel: (data) => ({
      legs: [],
      operator: data.attributes.operator ?? undefined,
      routeIdentifiers: routeIdentifierModel.toModel(data.attributes.routeIdentifiers),
      vendor: data.attributes.vendor,
      cabinClass: data.attributes.cabinClassName,
      legType: undefined,
    }),
  },
);
export type BookingDetailsModel = Infer<typeof bookingDetailsModel>;
export type BookingDetailsSchema = Infer<typeof bookingDetailsModel, "schema">;

const bookingRelationships: z.ZodType<{
  order: { data: Infer<typeof orderModel, "identifier"> };
  status: { data: z.infer<typeof bookingStatusIdentifier> };
  details: { data: Infer<typeof bookingDetailsModel, "identifier">[] };
}> = relationship({
  order: z.lazy(() => orderModel.identifier),
  status: bookingStatusIdentifier,
  details: z.array(z.lazy(() => bookingDetailsModel.identifier)),
});

const bookingBase = z.object({
  id: z.string(),
  price: priceModel.model,
  operatorReferences: z.array(z.string()),
  externalReference: z.string().optional(),
  status: bookingStatusIdentifier.shape.id,
});

const bookingExt: z.ZodType<
  z.infer<typeof bookingBase> & {
    order?: Infer<typeof orderModel>;
    details?: Infer<typeof bookingDetailsModel>;
  }
> = bookingBase.extend({
  order: z.lazy(() => orderModel.model.optional()),
  details: z.lazy(() => bookingDetailsModel.model.optional()),
});

export const bookingModel = getSchemaModel(
  z.object({
    id: z.string(),
    type: z.enum(["trip-bookings"]),
    attributes: z.object({
      totalPrice: priceModel.schema,
      operatorBookingReferences: z.array(z.string()),
      externalReference: z.string(),
    }),
    relationships: bookingRelationships,
    links: links(["self"]),
  }),
  bookingExt,
  {
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
  },
);
export type BookingModel = Infer<typeof bookingModel>;
export type BookingSchema = Infer<typeof bookingModel, "schema">;

export type BookingIncludes =
  | OrderSchema
  | JourneySchema
  | BookingDetailsSchema
  | CabinClassSchema
  | LegTypeSchema;
