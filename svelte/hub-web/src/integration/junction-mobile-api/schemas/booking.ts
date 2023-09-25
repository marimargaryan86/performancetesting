import { z } from "zod";
import { getSchemaModel, links, relationship, type Infer } from "../../common/schema-model.server";
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

const bookingDetailsRelationships: z.ZodType<{
  cabinClass: { data: CabinClassIdentifier };
  legType: { data: LegTypeIdentifier };
  booking: { data: BookingIdentifier };
}> = relationship({
  cabinClass: cabinClassModel.identifier,
  legType: legTypeModel.identifier,
  booking: z.lazy(() => bookingModel.identifier),
});

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
> = bookingDetailsModelBase.extend({
  booking: z.lazy(() => bookingModel.model).optional(),
});

export const bookingDetailsModel = getSchemaModel(
  z.object({
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
    links: links(["self"]),
  }),
  bookingDetailsModelExt,
  {
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
  },
);
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
}> = relationship({
  status: bookingStatusIdentifier,
  details: z.array(bookingDetailsModel.identifier),
  order: z.lazy(() => orderModel.identifier),
});

export const bookingModelBase = z.object({
  id: z.string(),
  price: priceModel.model,
  operatorBookingReferences: z.array(z.string()),
  externalReference: z.string(),
  ticketUrl: z.string().optional(),
  status: bookingStatusIdentifier.shape.id,
  details: z.array(bookingDetailsModel.model),
});

const bookingModelExt: z.ZodType<z.infer<typeof bookingModelBase> & { order?: OrderModel }> =
  bookingModelBase.extend({ order: z.lazy(() => orderModel.model).optional() });

export const bookingModel = getSchemaModel(
  z.object({
    id: z.string().uuid(),
    type: z.enum(["trip-bookings"]),
    attributes: z.object({
      totalPrice: priceModel.schema,
      operatorBookingReferences: z.array(z.string()),
      externalReference: z.string(),
      ticketUrl: z.string().optional(),
    }),
    relationships: bookingRelationships,
    links: links(["self"]),
  }),
  bookingModelExt,
  {
    toModel: (data): z.infer<typeof bookingModelExt> => ({
      id: data.id,
      details: [],
      externalReference: data.attributes.externalReference,
      operatorBookingReferences: data.attributes.operatorBookingReferences,
      ticketUrl: data.attributes.ticketUrl,
      price: priceModel.toModel(data.attributes.totalPrice),
      status: data.relationships.status.data.id,
      order: undefined,
    }),
  },
);
export type BookingModel = Infer<typeof bookingModel>;
export type BookingSchema = Infer<typeof bookingModel, "schema">;
export type BookingIdentifier = Infer<typeof bookingModel, "identifier">;
