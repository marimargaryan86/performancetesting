import integrationInstancesServer from "integration-instances";
import type { OrderModel } from "integration/junction-mobile-api/schemas/order";
import type { PaginatedData } from "models/common";

export async function load(): Promise<{ orders: PaginatedData<OrderModel> }> {
  return {
    orders: await integrationInstancesServer.junctionMobileApi.orders.listOrders(),
  };
}
