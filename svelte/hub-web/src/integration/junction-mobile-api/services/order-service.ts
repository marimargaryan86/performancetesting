import JunctionMobileApiService from "./junction-mobile-api-service";
import {
  createOrderModel,
  type CreateOrderModel,
  type CreateOrderSchema,
  type OrderIncludes,
  type OrderModel,
  type OrderSchema,
} from "../schemas/order";
import { getRandomAlphaNumericString } from "utils/random";
import { parseOrderSchema } from "../parsers/order";
import type { PaginatedData } from "models/common";
import { parseIncluded } from "../parsers/included";
import { ensureJunctionError } from "integration/common/junction-error";
import { z } from "zod";

export class OrderService extends JunctionMobileApiService {
  async listOrders(cursor?: string, limit = 100): Promise<PaginatedData<OrderModel>> {
    const resp = await this.makeRequest<{
      data: OrderSchema[];
      included?: OrderIncludes[];
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

    const included = parseIncluded(resp.json.included);

    return {
      data: resp.json.data.map((item) => parseOrderSchema(item, included)),
      // cursor: OrderService.getCursor(data),
      cursor: undefined,
    };
  }

  async createOrder(data: CreateOrderModel): Promise<OrderModel> {
    try {
      const resp = await this.makeRequest<{ data: OrderSchema }>("/orders", {
        method: "POST",
        data: { data: createOrderModel.toSchema(data) },
        headers: { "Session-Token": getRandomAlphaNumericString(32) },
      });

      return parseOrderSchema(resp.json.data);
    } catch (err) {
      if (ensureJunctionError<{ data: CreateOrderSchema }>(err)) {
        const error = new z.ZodError<CreateOrderModel>([]);

        err.json?.errors.map((item) => {
          if (item.source?.pointer === "/data/attributes/contactDetails/phoneNumber") {
            error.addIssue({
              code: "custom",
              message: "Invalid phone number",
              path: ["contactDetails", "phone", "number"],
            });
          }

          throw error;
        });
      }

      throw err;
    }
  }

  async getOrder(id: string): Promise<OrderModel> {
    const resp = await this.makeRequest<{
      data: OrderSchema;
      included?: OrderIncludes[];
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

    const included = parseIncluded(resp.json.included);

    return parseOrderSchema(resp.json.data, included);
  }
}
