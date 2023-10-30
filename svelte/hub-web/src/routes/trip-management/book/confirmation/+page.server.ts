import integrationInstances from "integration-instances";
import type { OrderMarkupsModel, OrderModel } from "integration/junction-mobile-api/schemas/order";
import { getSession } from "utils/auth";
import utils from "../../../integration/trip-management/utils.server";
import { redirect } from "@sveltejs/kit";
import routeConfig from "routeConfig";

export function load(event): { order: Promise<OrderModel>; markups: Promise<OrderMarkupsModel> } {
  try {
    const bookingSession = utils.getBookingSession(event);

    if (!bookingSession.order) {
      throw new Error();
    }

    return {
      order: integrationInstances.junctionMobileApi.orders.getOrder({
        session: getSession(event),
        id: bookingSession.order.id,
      }),
      markups: integrationInstances.junctionMobileApi.orders.getOrderMarkups({
        session: getSession(event),
        id: bookingSession.order.id,
      }),
    };
  } catch {
    throw redirect(303, routeConfig.routes.tripManagement.routes.book.root);
  }
}
