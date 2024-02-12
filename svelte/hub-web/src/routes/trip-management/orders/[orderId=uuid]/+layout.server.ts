import integrationInstances from "~/integration-instances";
import type * as HubSchemas from "~/integration/junction-hub-api/schemas";

export function load(event): { order: Promise<HubSchemas.Order> } {
  return {
    order: integrationInstances.junctionHubApi.orders.get({
      session: event.locals.session,
      id: event.params.orderId,
    }),
  };
}
