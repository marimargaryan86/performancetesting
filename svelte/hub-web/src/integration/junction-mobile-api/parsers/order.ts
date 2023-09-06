import { orderModel, type OrderModel, type OrderSchema } from "../schemas/order";
import type { JourneyModel } from "../schemas/journey";
import type { BookingModel } from "../schemas/booking";

export function parseOrderSchema(
  data: OrderSchema,
  included: {
    journeys: JourneyModel[];
    bookings: BookingModel[];
  },
): OrderModel {
  const parsed = orderModel.toModel(data);

  return {
    ...parsed,
    bookings: included.bookings.filter((item) => parsed.bookingIds.includes(item.id)),
    journey: included.journeys.find((item) => item.id === data.relationships.journey.data.id),
  };
}
