import type { orderModel } from "../schemas/order";
import type { cabinClassModel, legTypeModel } from "../schemas/offer";
import type { Infer } from "../schema-model.server";
import { bookingDetailsModel, bookingModel } from "../schemas/booking";

export function parseBookingDetailsSchema(
  data: Infer<typeof bookingDetailsModel, "schema">,
  included: {
    bookings: Infer<typeof bookingModel>[];
    cabinClasses: Infer<typeof cabinClassModel>[];
    legTypes: Infer<typeof legTypeModel>[];
  },
): Infer<typeof bookingDetailsModel> {
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
  data: Infer<typeof bookingModel, "schema">,
  included: {
    bookingDetails: Infer<typeof bookingDetailsModel>[];
    orders: Infer<typeof orderModel>[];
  },
): Infer<typeof bookingModel> {
  const bookingDetailsIds = data.relationships.details.data.map((item) => item.id);

  return {
    ...bookingModel.toModel(data),
    details: included.bookingDetails.filter((item) => bookingDetailsIds.includes(item.id)),
    order: included.orders.find((item) => item.id === data.relationships.order.data.id),
  };
}
