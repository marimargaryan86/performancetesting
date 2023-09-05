import { orderModel } from "../schemas/order";
import type { journeyModel } from "../schemas/journey";
import type { Infer } from "../schema-model.server";
import type { bookingModel } from "../schemas/booking";

export function parseOrderSchema(
  data: Infer<typeof orderModel, "schema">,
  included: {
    journeys: Infer<typeof journeyModel>[];
    bookings: Infer<typeof bookingModel>[];
  },
): Infer<typeof orderModel> {
  const parsed = orderModel.toModel(data);

  return {
    ...parsed,
    bookings: included.bookings.filter((item) => parsed.bookingIds.includes(item.id)),
    journey: included.journeys.find((item) => item.id === data.relationships.journey.data.id),
  };
}
