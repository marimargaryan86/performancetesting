import integrationInstances from "~/integration-instances";
import { redirect } from "@sveltejs/kit";
import routeConfig from "$lib/route-config";
import type * as MobileSchemas from "~/integration/junction-mobile-api/schemas";
import { getCookie } from "$lib/booking-manager/booking-manager";

export async function load(event): Promise<{
  order: MobileSchemas.Order;
  markups?: MobileSchemas.Markups;
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
    throw redirect(
      303,
      routeConfig.routes.tripManagement.routes.book.routes[event.params.searchType].root,
    );
  }
}
