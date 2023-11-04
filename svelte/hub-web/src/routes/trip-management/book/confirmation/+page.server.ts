import integrationInstances from "integration-instances";
import type { Order } from "integration/junction-mobile-api/schemas/order";
import { getSession } from "utils/auth";
import utils from "../../../integration/trip-management/utils.server";
import { redirect } from "@sveltejs/kit";
import routeConfig from "routeConfig";
import type { Markups } from "integration/junction-mobile-api/schemas/markups";

export function load(event): {
  order: Promise<Order>;
  markups: Promise<Markups | undefined>;
} {
  try {
    const bookingSession = utils.getBookingSession(event);

    if (!bookingSession.order) {
      throw new Error();
    }

    return {
      order: integrationInstances.junctionMobileApi.orders.get({
        session: getSession(event),
        id: bookingSession.order.id,
      }),
      markups: integrationInstances.junctionMobileApi.orders
        .getMarkups({
          session: getSession(event),
          orderId: bookingSession.order.id,
        })
        .catch(() => undefined),
    };
  } catch {
    throw redirect(303, routeConfig.routes.tripManagement.routes.book.root);
  }
}
