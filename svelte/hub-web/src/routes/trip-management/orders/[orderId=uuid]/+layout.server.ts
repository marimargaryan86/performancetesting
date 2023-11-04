import integrationInstances from "integration-instances";
import type { Order } from "integration/junction-hub-api/schemas/order";
import { getSession } from "utils/auth";

export function load(event): { order: Promise<Order> } {
  return {
    order: integrationInstances.junctionHubApi.orders.get({
      session: getSession(event),
      id: event.params.orderId,
    }),
  };
}
