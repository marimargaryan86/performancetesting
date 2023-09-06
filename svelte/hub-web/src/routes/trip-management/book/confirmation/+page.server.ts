import { redirect } from "@sveltejs/kit";
import { getSearchData, setSearchData } from "../common";
import integrationInstances from "integration-instances";
import type { orderModel } from "integration/junction-mobile-api/schemas/order";
import type { Infer } from "integration/junction-mobile-api/schema-model.server";
import routeConfig from "routeConfig";

export function load(event): { order: Promise<Infer<typeof orderModel>> } {
  const searchData = getSearchData(event);

  if (!searchData?.orderId) {
    setSearchData(undefined, event);

    throw redirect(303, routeConfig.tripManagement.book.root);
  }

  return {
    order: integrationInstances.junctionMobileApi.orders.getOrder(searchData.orderId),
  };
}
