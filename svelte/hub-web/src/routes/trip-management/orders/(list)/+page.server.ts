import integrationInstancesServer from "integration-instances";
import type { OrderModel } from "integration/junction-mobile-api/schemas/order";
import type { PaginatedData } from "models/common";
import { getSession } from "utils/auth";

export function load(event): { orders: Promise<PaginatedData<OrderModel>> } {
  return {
    orders: integrationInstancesServer.junctionMobileApi.orders.listOrders({
      session: getSession(event),
    }),
  };
}
