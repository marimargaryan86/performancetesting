import integrationInstances from "integration-instances";
import type { OrderModel } from "integration/junction-mobile-api/schemas/order";

export function load(event): { order: Promise<OrderModel> } {
  return {
    order: integrationInstances.junctionMobileApi.orders.getOrder(event.params.orderId),
  };
}
