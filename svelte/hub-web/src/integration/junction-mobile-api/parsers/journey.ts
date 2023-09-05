import { journeyModel } from "../schemas/journey";
import type { Infer } from "../schema-model.server";
import type { orderModel } from "../schemas/order";

export function parseJourneySchema(
  data: Infer<typeof journeyModel, "schema">,
  included: { orders: Infer<typeof orderModel>[] },
): Infer<typeof journeyModel> {
  const orderIds = data.relationships.orders.data.map((item) => item.id);

  return {
    ...journeyModel.toModel(data),
    orders: included.orders.filter((item) => orderIds.includes(item.id)),
  };
}
