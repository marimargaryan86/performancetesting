import { redirect } from "@sveltejs/kit";
import { getSearchData, setSearchData } from "../common";
import integrationInstances from "integration-instances";
import type { OrderModel } from "integration/junction-mobile-api/schemas/order";
import routeConfig from "routeConfig";

export function load(event): { order: Promise<OrderModel> } {
  const searchData = getSearchData(event);

  if (!searchData?.orderId) {
    setSearchData(undefined, event);

    throw redirect(303, routeConfig.tripManagement.book.root);
  }

  return {
    order: integrationInstances.junctionMobileApi.orders.getOrder(searchData.orderId),
  };
}
