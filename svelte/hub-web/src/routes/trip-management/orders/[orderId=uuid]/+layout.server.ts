import integrationInstances from "~/integration-instances";
import type { Order } from "~/integration/junction-hub-api/schemas/order";

export function load(event): { order: Promise<Order> } {
  return {
    order: integrationInstances.junctionHubApi.orders.get({
      session: event.locals.session,
      id: event.params.orderId,
    }),
  };
}
