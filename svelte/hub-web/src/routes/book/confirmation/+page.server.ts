import { error } from "@sveltejs/kit";
import { getSearchData } from "../common";
import integrationInstancesServer from "integration-instances-server";
import type { OrderModel } from "models/booking/order";

export function load(event): { order: Promise<OrderModel> } {
  const searchData = getSearchData(event);

  if (!searchData) {
    throw error(400, { message: "No search data found" });
  }

  if (!searchData.orderId) {
    throw error(400, { message: "No order ID found" });
  }

  return {
    order: integrationInstancesServer.junctionMobileApi.orders.getOrder(searchData.orderId),
  };
}
