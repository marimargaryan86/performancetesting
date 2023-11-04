import integrationInstances from "integration-instances";
import type { Order } from "integration/junction-mobile-api/schemas/order";
import { getSession } from "utils/auth";

export function load(event): { order: Promise<Order> } {
  return {
    order: integrationInstances.junctionMobileApi.orders.getOrder({
      session: getSession(event),
      id: event.params.orderId,
    }),
  };
}
