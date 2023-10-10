import integrationInstances from "integration-instances";
import type { OrderModel } from "integration/junction-mobile-api/schemas/order";
import { getSession } from "utils/auth";

export function load(event): { order: Promise<OrderModel> } {
  return {
    order: integrationInstances.junctionMobileApi.orders.getOrder({
      session: getSession(event),
      id: event.params.orderId,
    }),
  };
}
