import { z } from "zod";
import {
  cabinClassModel,
  legTypeModel,
  routeIdentifierModel,
  offerSegmentLegModel,
  type LegTypeIdentifier,
  type CabinClassIdentifier,
} from "./offer";
import { orderModel, type OrderIdentifier, type OrderModel } from "./order";
import { priceModel } from "./price";
import schemaModel, { type Infer } from "utils/schema-model";

const bookingDetailsRelationships: z.ZodType<{
  cabinClass: { data: CabinClassIdentifier };
  legType: { data: LegTypeIdentifier };
  booking: { data: BookingIdentifier };
}> = z.lazy(() =>
  schemaModel.relationships({
    cabinClass: cabinClassModel.identifier,
    legType: legTypeModel.identifier,
    booking: bookingModel.identifier,
  }),
);

const bookingDetailsModelBase = z.object({
  id: z.string(),
  cabinClassName: z.string(),
  vendor: z.string(),
  operator: z.string().optional(),
  routeIdentifiers: routeIdentifierModel.model,
  legs: z.array(offerSegmentLegModel.model),
  bookingId: z.string(),
  cabinClass: cabinClassModel.model.optional(),
  legType: legTypeModel.model.optional(),
});

const bookingDetailsModelExt: z.ZodType<
  z.infer<typeof bookingDetailsModelBase> & { booking?: BookingModel }
> = z.lazy(() =>
  bookingDetailsModelBase.extend({
    booking: bookingModel.model.optional(),
  }),
);

export const bookingDetailsModel = schemaModel.create({
  schema: z.object({
    id: z.string().uuid(),
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
  model: bookingDetailsModelExt,
  toModel: (data): z.infer<typeof bookingDetailsModelExt> => ({
    id: data.id,
    cabinClassName: data.attributes.cabinClassName,
    legs: data.attributes.legs.map(offerSegmentLegModel.toModel),
    operator: data.attributes.operator ?? undefined,
    routeIdentifiers: routeIdentifierModel.toModel(data.attributes.routeIdentifiers),
    vendor: data.attributes.vendor,
    bookingId: data.relationships.booking.data.id,
    booking: undefined,
    cabinClass: undefined,
    legType: undefined,
  }),
});
export type BookingDetailsModel = Infer<typeof bookingDetailsModel>;
export type BookingDetailsSchema = Infer<typeof bookingDetailsModel, "schema">;
export type BookingDetailsIdentifier = Infer<typeof bookingDetailsModel, "identifier">;

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
export type BookingStatus = z.infer<typeof bookingStatusIdentifier>["id"];

const bookingRelationships: z.ZodType<{
  status: { data: z.infer<typeof bookingStatusIdentifier> };
  details: { data: BookingDetailsIdentifier[] };
  order: { data: OrderIdentifier };
}> = z.lazy(() =>
  schemaModel.relationships({
    status: bookingStatusIdentifier,
    details: z.array(bookingDetailsModel.identifier),
    order: orderModel.identifier,
  }),
);

export const bookingModelBase = z.object({
  id: z.string(),
  price: priceModel.model,
  operatorBookingReferences: z.array(z.string()),
  externalReference: z.string(),
  ticketUrls: z.array(z.string()).optional(),
  status: bookingStatusIdentifier.shape.id,
  details: z.array(bookingDetailsModel.model),
});

const bookingModelExt: z.ZodType<z.infer<typeof bookingModelBase> & { order?: OrderModel }> =
  z.lazy(() => bookingModelBase.extend({ order: orderModel.model.optional() }));

export const bookingModel = schemaModel.create({
  schema: z.object({
    id: z.string().uuid(),
    type: z.enum(["trip-bookings"]),
    attributes: z.object({
      totalPrice: priceModel.schema,
      operatorBookingReferences: z.array(z.string()),
      externalReference: z.string(),
      ticketUrls: z.array(z.string()).optional(),
    }),
    relationships: bookingRelationships,
    links: schemaModel.links({ self: true }),
  }),
  model: bookingModelExt,
  toModel: (data): z.infer<typeof bookingModelExt> => ({
    id: data.id,
    details: [],
    externalReference: data.attributes.externalReference,
    operatorBookingReferences: data.attributes.operatorBookingReferences,
    ticketUrls: data.attributes.ticketUrls,
    price: priceModel.toModel(data.attributes.totalPrice),
    status: data.relationships.status.data.id,
    order: undefined,
  }),
});
export type BookingModel = Infer<typeof bookingModel>;
export type BookingSchema = Infer<typeof bookingModel, "schema">;
export type BookingIdentifier = Infer<typeof bookingModel, "identifier">;
