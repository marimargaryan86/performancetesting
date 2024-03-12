import integrationInstances from "~/integration-instances";
import type * as HubSchemas from "~/integration/junction-hub-api/schemas";

export async function load(event): Promise<{ order: HubSchemas.Order }> {
  return {
    order: await integrationInstances.junctionHubApi.orders.get({
      session: event.locals.session,
      id: event.params.orderId,
    }),
  };
}
