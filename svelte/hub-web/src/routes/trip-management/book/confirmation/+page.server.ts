import { error } from "@sveltejs/kit";
import { getSearchData } from "../common";
import integrationInstances from "integration-instances";
import type { orderModel } from "integration/junction-mobile-api/schemas/order";
import type { Infer } from "integration/junction-mobile-api/schema-model.server";

export function load(event): { order: Promise<Infer<typeof orderModel>> } {
  const searchData = getSearchData(event);

  if (!searchData) {
    throw error(400, { message: "No search data found" });
  }

  if (!searchData.orderId) {
    throw error(400, { message: "No order ID found" });
  }

  return {
    order: integrationInstances.junctionMobileApi.orders.getOrder(searchData.orderId),
  };
}
