import integrationInstances from "integration-instances";
import type { OrderModel } from "integration/junction-mobile-api/schemas/order";
import bookingManager from "../booking-manager.server";
import { getSession } from "utils/auth";

export function load(event): { order: Promise<OrderModel> } {
  const searchData = bookingManager.getSearchData(event);

  if (!searchData.orderId) {
    throw bookingManager.rootRedirect(event);
  }

  return {
    order: integrationInstances.junctionMobileApi.orders.getOrder({
      session: getSession(event),
      id: searchData.orderId,
    }),
  };
}
