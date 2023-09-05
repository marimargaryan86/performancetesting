import JunctionMobileApiService from "./junction-mobile-api-service";
import { createOrderModel, type OrderIncludes, type orderModel } from "../schemas/order";
import { getRandomAlphaNumericString } from "utils/random";
import { parseOrderSchema } from "../parsers/order";
import type { PaginatedData } from "models/common";
import type { Infer } from "../schema-model.server";
import { parseIncluded } from "../parsers/included";

export class OrderService extends JunctionMobileApiService {
  async listOrders(cursor?: string, limit = 100): Promise<PaginatedData<Infer<typeof orderModel>>> {
    const resp = await this.makeRequest<{
      data: Infer<typeof orderModel, "schema">[];
      included?: OrderIncludes;
      links: { next: string };
    }>("/orders", {
      queryParams: {
        include: [
          "journey",
          "bookings",
          "bookings.details",
          "bookings.details.cabinClass",
          "bookings.details.legType",
        ].join(","),
        "page[limit]": limit,
        "page[cursor]": cursor,
      },
    });

    if (resp.status !== 200) {
      throw new Error("Failed to fetch orders");
    }

    const data = await resp.json();
    const included = parseIncluded(data.included);

    return {
      data: data.data.map((item) => parseOrderSchema(item, included)),
      // cursor: OrderService.getCursor(data),
      cursor: undefined,
    };
  }

  async createOrder(data: Infer<typeof createOrderModel>): Promise<Infer<typeof orderModel>> {
    const resp = await this.makeRequest<
      { data: Infer<typeof orderModel, "schema"> },
      { data: Infer<typeof createOrderModel, "schema"> }
    >("/orders", {
      method: "POST",
      data: { data: createOrderModel.toSchema(data) },
      headers: { "Session-Token": getRandomAlphaNumericString(32) },
    });

    if (resp.status !== 201) {
      throw new Error("Order creation failed");
    }

    return parseOrderSchema((await resp.json()).data, { bookings: [], journeys: [] });
  }

  async getOrder(id: string): Promise<Infer<typeof orderModel>> {
    const resp = await this.makeRequest<{
      data: Infer<typeof orderModel, "schema">;
      included?: OrderIncludes;
    }>(`/orders/${id}`, {
      queryParams: {
        include: [
          "journey",
          "bookings",
          "bookings.details",
          "bookings.details.cabinClass",
          "bookings.details.legType",
        ].join(","),
      },
    });

    if (resp.status === 404) {
      throw new Error("Booking not found");
    }

    const data = await resp.json();
    const included = parseIncluded(data.included);

    return parseOrderSchema(data.data, included);
  }
}
