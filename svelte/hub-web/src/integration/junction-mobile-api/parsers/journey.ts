import { journeyModel, type JourneyModel, type JourneySchema } from "../schemas/journey";
import type { OrderModel } from "../schemas/order";

export function parseJourneySchema(
  data: JourneySchema,
  included: { orders: OrderModel[] },
): JourneyModel {
  const orderIds = data.relationships.orders.data.map((item) => item.id);

  return {
    ...journeyModel.toModel(data),
    orders: included.orders.filter((item) => orderIds.includes(item.id)),
  };
}
