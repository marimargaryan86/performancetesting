import integrationInstancesServer from "integration-instances";
import type { Infer } from "integration/junction-mobile-api/schema-model.server";
import type { orderModel } from "integration/junction-mobile-api/schemas/order";
import type { PaginatedData } from "models/common";

export async function load(): Promise<{ orders: PaginatedData<Infer<typeof orderModel>> }> {
  return {
    orders: await integrationInstancesServer.junctionMobileApi.orders.listOrders(),
  };
}
