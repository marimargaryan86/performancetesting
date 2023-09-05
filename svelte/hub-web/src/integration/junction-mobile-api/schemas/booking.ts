import { z } from "zod";
import { getSchemaModel, links, relationship, type Infer } from "../schema-model.server";
import { cabinClassModel, legTypeModel, routeIdentifierModel, offerSegmentLegModel } from "./offer";
import { orderModel } from "./order";
import { priceModel } from "./price";

const bookingDetailsRelationships: z.ZodType<{
  cabinClass: { data: Infer<typeof cabinClassModel, "identifier"> };
  legType: { data: Infer<typeof legTypeModel, "identifier"> };
  booking: { data: Infer<typeof bookingModel, "identifier"> };
}> = relationship({
  cabinClass: cabinClassModel.schema.pick({ id: true, type: true }),
  legType: legTypeModel.schema.pick({ id: true, type: true }),
  booking: z.lazy(() => bookingModel.schema.pick({ id: true, type: true })),
});

const bookingDetailsModelBase = z.object({
  id: z.string(),
  cabinClassName: z.string(),
  vendor: z.string(),
  operator: z.string(),
  routeIdentifiers: routeIdentifierModel.model,
  legs: z.array(offerSegmentLegModel.model),
  bookingId: z.string(),
  cabinClass: cabinClassModel.model.optional(),
  legType: legTypeModel.model.optional(),
});

const bookingDetailsModelExt: z.ZodType<
  z.infer<typeof bookingDetailsModelBase> & { booking?: Infer<typeof bookingModel> }
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
      operator: z.string(),
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
      operator: data.attributes.operator,
      routeIdentifiers: routeIdentifierModel.toModel(data.attributes.routeIdentifiers),
      vendor: data.attributes.vendor,
      bookingId: data.relationships.booking.data.id,
      booking: undefined,
      cabinClass: undefined,
      legType: undefined,
    }),
  },
);

const bookingRelationships: z.ZodType<{
  status: { data: { id: string; type: "booking-statuses" } };
  details: { data: Infer<typeof bookingDetailsModel, "identifier">[] };
  order: { data: Infer<typeof orderModel, "identifier"> };
}> = relationship({
  status: z.object({ id: z.string(), type: z.enum(["booking-statuses"]) }),
  details: z.array(bookingDetailsModel.schema.pick({ id: true, type: true })),
  order: z.lazy(() => orderModel.schema.pick({ id: true, type: true })),
});

export const bookingModelBase = z.object({
  id: z.string(),
  price: priceModel.model,
  operatorBookingReferences: z.array(z.string()),
  externalReference: z.string(),
  status: z.string(),
  details: z.array(bookingDetailsModel.model),
});

const bookingModelExt: z.ZodType<
  z.infer<typeof bookingModelBase> & { order?: Infer<typeof orderModel> }
> = bookingModelBase.extend({ order: z.lazy(() => orderModel.model).optional() });

export const bookingModel = getSchemaModel(
  z.object({
    id: z.string().uuid(),
    type: z.enum(["trip-bookings"]),
    attributes: z.object({
      totalPrice: priceModel.schema,
      operatorBookingReferences: z.array(z.string()),
      externalReference: z.string(),
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
      price: priceModel.toModel(data.attributes.totalPrice),
      status: data.relationships.status.data.id,
      order: undefined,
    }),
  },
);
