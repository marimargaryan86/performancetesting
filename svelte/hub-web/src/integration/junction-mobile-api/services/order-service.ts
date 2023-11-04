import JunctionMobileApiService from "./junction-mobile-api-service";
import type { PaginatedData } from "models/common";
import { JunctionError, ensureJunctionError } from "integration/common/junction-error";
import { z } from "zod";
import type { SessionModel } from "models/user";
import {
  orderParser,
  type Order,
  type OrderSchema,
  type OrderCreate,
  type OrderCreateSchema,
} from "../schemas/order";
import { parseIncluded, type IncludedSchemas } from "../schemas/included";
import {
  markupsParser,
  type Markups,
  type MarkupsSchema,
  type MarkupsCreate,
} from "../schemas/markups";

export class OrderService extends JunctionMobileApiService {
  async listOrders({
    session,
    cursor,
    limit = 100,
  }: {
    session: SessionModel;
    cursor?: string;
    limit?: number;
  }): Promise<PaginatedData<Order>> {
    const resp = await this.makeRequest<{
      data: OrderSchema[];
      included?: IncludedSchemas | null;
    }>("/orders", {
      queryParams: {
        include: [
          "journey",
          "bookings",
          "bookings.details",
          "bookings.details.cabinClass",
          "bookings.details.legType",
          "bookings.bookingCancellation",
        ].join(","),
        "page[limit]": limit,
        "page[cursor]": cursor,
      },
      session,
    });

    const parsed = parseIncluded([...(resp.json.included ?? []), ...resp.json.data]);

    return {
      data: parsed.orders ?? [],
      cursor: undefined,
    };
  }

  async createOrder({
    session,
    data,
  }: {
    session: SessionModel;
    data: OrderCreate;
  }): Promise<Order> {
    try {
      const resp = await this.makeRequest<{ data: OrderSchema }>("/orders", {
        method: "POST",
        data: { data: orderParser.toCreateSchema(data) },
        session,
      });

      return orderParser.toModel(resp.json.data);
    } catch (err) {
      if (ensureJunctionError<{ data: OrderCreateSchema }>(err)) {
        const error = new z.ZodError<OrderCreate>([]);

        err.json?.errors.map((item) => {
          if (item.source?.pointer === "/data/attributes/contactDetails/phoneNumber") {
            error.addIssue({
              code: "custom",
              message: "Invalid phone number",
              path: ["contact", "phone"],
            });
          }

          throw error;
        });
      }

      throw err;
    }
  }

  async getOrder({ id, session }: { id: string; session: SessionModel }): Promise<Order> {
    const resp = await this.makeRequest<{
      data: OrderSchema;
      included?: IncludedSchemas;
    }>(`/orders/${id}`, {
      queryParams: {
        include: [
          "journey",
          "bookings",
          "bookings.details",
          "bookings.details.cabinClass",
          "bookings.details.legType",
          "bookings.bookingCancellation",
        ].join(","),
      },
      session,
    });

    const parsed = parseIncluded([...(resp.json.included ?? []), resp.json.data]);
    const order = parsed.orders?.find((item) => item.id === id);

    if (!order) {
      throw new JunctionError({ status: 404, statusText: "Not found" });
    }

    return order;
  }

  async createOrderMarkups({
    session,
    data,
  }: {
    session: SessionModel;
    data: MarkupsCreate;
  }): Promise<Markups> {
    const resp = await this.makeRequest<{ data: MarkupsSchema }>("/orders/markups", {
      method: "POST",
      data: { data: markupsParser.toCreateSchema(data) },
      session,
    });

    return markupsParser.toModel(resp.json.data);
  }

  async getOrderMarkups({ id, session }: { id: string; session: SessionModel }): Promise<Markups> {
    const resp = await this.makeRequest<{ data: MarkupsSchema }>(`/orders/${id}/markup`, {
      session,
    });

    return markupsParser.toModel(resp.json.data);
  }
}
