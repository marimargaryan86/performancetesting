import integrationInstances from "~/integration-instances";
import type { Order } from "~/integration/junction-mobile-api/schemas/order";
import { redirect } from "@sveltejs/kit";
import routeConfig from "~/route-config";
import type { Markups } from "~/integration/junction-mobile-api/schemas/markups";
import { getCookie } from "../../../booking-flow";

export async function load(event): Promise<{
  order: Order;
  markups?: Markups;
}> {
  const { session } = event.locals;

  try {
    const bookingSession = getCookie("payment", event);

    const [order, markups] = await Promise.all([
      integrationInstances.junctionMobileApi.orders.get({ session, id: bookingSession.order.id }),
      /* eslint-disable indent */
      bookingSession.markups
        ? integrationInstances.junctionMobileApi.orders
            .getMarkups({ session: event.locals.session, orderId: bookingSession.order.id })
            .catch(() => undefined)
        : undefined,
      /* eslint-enable indent */
    ]);

    return { order, markups };
  } catch {
    throw redirect(303, routeConfig.routes.tripManagement.routes.book.routes.train.root);
  }
}
