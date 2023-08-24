import type { BookingDetailsSchema, BookingSchema } from "../schemas/order";
import { parseOfferSegmentLegSchema } from "./offer";
import { parsePriceSchema } from "./money";
import type { BookingDetailsModel, BookingModel, OrderModel } from "models/booking/order";
import type { CabinClassModel, LegTypeModel } from "models/booking/offer";

export function parseBookingDetailsSchema(
  data: BookingDetailsSchema,
  included: {
    bookings: BookingModel[];
    cabinClasses: CabinClassModel[];
    legTypes: LegTypeModel[];
  },
): BookingDetailsModel {
  return {
    id: data.id,
    cabinClassName: data.attributes.cabinClassName,
    legs: data.attributes.legs.map(parseOfferSegmentLegSchema),
    operator: data.attributes.operator,
    routeIdentifiers: {
      vendor: data.attributes.routeIdentifiers.vendor,
      operator: data.attributes.routeIdentifiers.operator ?? undefined,
    },
    vendor: data.attributes.vendor,
    bookingId: data.relationships.booking.data.id,
    booking: included.bookings.find((item) => item.id === data.relationships.booking.data.id),
    cabinClass: included.cabinClasses.find(
      (item) => item.id === data.relationships.cabinClass.data.id,
    ),
    legType: included.legTypes.find((item) => item.id === data.relationships.legType.data.id),
  };
}

export function parseBookingSchema(
  data: BookingSchema,
  bookingDetails: BookingDetailsModel[],
  orders: OrderModel[],
): BookingModel {
  const bookingDetailsIds = data.relationships.details.data.map((item) => item.id);
  const details = bookingDetails.filter((item) => bookingDetailsIds.includes(item.id));

  return {
    id: data.id,
    details,
    externalReference: data.attributes.externalReference,
    operatorBookingReferences: data.attributes.operatorBookingReferences,
    price: parsePriceSchema(data.attributes.totalPrice),
    status: data.relationships.status.data.id,
    order: orders.find((item) => item.id === data.relationships.order.data.id),
  };
}
