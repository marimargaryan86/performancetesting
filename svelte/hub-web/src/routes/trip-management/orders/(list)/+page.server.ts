import integrationInstancesServer from "integration-instances";
import type { OrderModel } from "integration/junction-mobile-api/schemas/order";
import type { PaginatedData } from "models/common";

export function load(): { orders: Promise<PaginatedData<OrderModel>> } {
  return {
    orders: integrationInstancesServer.junctionMobileApi.orders.listOrders(),
  };
}
