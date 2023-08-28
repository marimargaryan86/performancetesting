import JunctionMobileApiService from "./junction-mobile-api-service";
import type { CreateOrderModel } from "../models";
import type {
  CreateOrderRequestSchema,
  CreateOrderResponseSchema,
  GetOrderResponseSchema,
  OrderSchema,
} from "../schemas/order";
import { getRandomAlphaNumericString } from "utils/random";
import {
  parseCreateOrderModel,
  parseCreateOrderResponseSchema,
  parseGetOrderResponseSchema,
  parseListOrdersResponseSchema,
} from "../parsers/order";
import type { OrderModel } from "models/booking/order";
import type { PaginatedData } from "models/common";

export class OrderService extends JunctionMobileApiService {
  async listOrders(cursor?: string, limit = 100): Promise<PaginatedData<OrderModel>> {
    const resp = await this.makeRequest<{
      data: OrderSchema[];
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

    return {
      data: parseListOrdersResponseSchema(data),
      // TODO: Fix
      // cursor: OrderService.getCursor(data),
      cursor: undefined,
    };
  }

  async createOrder(data: CreateOrderModel): Promise<OrderModel> {
    const resp = await this.makeRequest<CreateOrderResponseSchema, CreateOrderRequestSchema>(
      "/orders",
      {
        method: "POST",
        data: parseCreateOrderModel(data),
        headers: { "Session-Token": getRandomAlphaNumericString(32) },
      },
    );

    if (resp.status !== 201) {
      throw new Error("Order creation failed");
    }

    return parseCreateOrderResponseSchema(await resp.json());
  }

  async getOrder(id: string): Promise<OrderModel> {
    const resp = await this.makeRequest<GetOrderResponseSchema>(`/orders/${id}`, {
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

    return parseGetOrderResponseSchema(await resp.json());
  }
}
