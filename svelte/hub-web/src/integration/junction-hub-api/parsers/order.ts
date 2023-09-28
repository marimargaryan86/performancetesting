import { journeyModel, type JourneySchema } from "../schemas/journey";
import { orderModel, type OrderModel, type OrderSchema } from "../schemas/order";

export function parseOrder(order: OrderSchema, journeys: JourneySchema[]): OrderModel {
  return {
    ...orderModel.toModel(order),
    journeys: journeys.map(journeyModel.toModel),
  };
}
