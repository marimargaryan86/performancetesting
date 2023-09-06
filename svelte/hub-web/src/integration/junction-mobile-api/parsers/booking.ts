import type { OrderModel } from "../schemas/order";
import type { CabinClassModel, LegTypeModel } from "../schemas/offer";
import {
  bookingDetailsModel,
  bookingModel,
  type BookingDetailsModel,
  type BookingDetailsSchema,
  type BookingModel,
  type BookingSchema,
} from "../schemas/booking";

export function parseBookingDetailsSchema(
  data: BookingDetailsSchema,
  included: {
    bookings: BookingModel[];
    cabinClasses: CabinClassModel[];
    legTypes: LegTypeModel[];
  },
): BookingDetailsModel {
  return {
    ...bookingDetailsModel.toModel(data),
    booking: included.bookings.find((item) => item.id === data.relationships.booking.data.id),
    cabinClass: included.cabinClasses.find(
      (item) => item.id === data.relationships.cabinClass.data.id,
    ),
    legType: included.legTypes.find((item) => item.id === data.relationships.legType.data.id),
  };
}

export function parseBookingSchema(
  data: BookingSchema,
  included: {
    bookingDetails: BookingDetailsModel[];
    orders: OrderModel[];
  },
): BookingModel {
  const bookingDetailsIds = data.relationships.details.data.map((item) => item.id);

  return {
    ...bookingModel.toModel(data),
    details: included.bookingDetails.filter((item) => bookingDetailsIds.includes(item.id)),
    order: included.orders.find((item) => item.id === data.relationships.order.data.id),
  };
}
