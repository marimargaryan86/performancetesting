import JunctionMobileApiService from "./junction-mobile-api-service";
import {
  createOrderModel,
  createOrderMarkupsModel,
  type CreateOrderMarkupsModel,
  type CreateOrderModel,
  type CreateOrderSchema,
  type OrderIncludes,
  type OrderMarkupsModel,
  type OrderMarkupsSchema,
  type OrderModel,
  type OrderSchema,
} from "../schemas/order";
import { getRandomAlphaNumericString } from "utils/random";
import { parseOrderMarkupsSchema, parseOrderSchema } from "../parsers/order";
import type { PaginatedData } from "models/common";
import { parseIncluded } from "../parsers/included";
import { ensureJunctionError } from "integration/common/junction-error";
import { z } from "zod";
import type { SessionModel } from "models/user";

export class OrderService extends JunctionMobileApiService {
  async listOrders({
    session,
    cursor,
    limit = 100,
  }: {
    session: SessionModel;
    cursor?: string;
    limit?: number;
  }): Promise<PaginatedData<OrderModel>> {
    const resp = await this.makeRequest<{
      data: OrderSchema[];
      included?: OrderIncludes[] | null;
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
      session,
    });

    const included = parseIncluded(resp.json.included);

    return {
      data: resp.json.data.map((item) => parseOrderSchema(item, included)),
      // cursor: OrderService.getCursor(data),
      cursor: undefined,
    };
  }

  async createOrder({
    session,
    data,
  }: {
    session: SessionModel;
    data: CreateOrderModel;
  }): Promise<OrderModel> {
    try {
      const resp = await this.makeRequest<{ data: OrderSchema }>("/orders", {
        method: "POST",
        data: { data: createOrderModel.toSchema(data) },
        headers: { "Session-Token": getRandomAlphaNumericString(32) },
        session,
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

  /**
   * TODO: Docs here.
   */
  async createOrderMarkups({
    session,
    data,
  }: {
    session: SessionModel;
    data: CreateOrderMarkupsModel;
  }): Promise<OrderMarkupsModel> {
    try {
      const resp = await this.makeRequest<{ data: OrderMarkupsSchema }>("/orders/markups", {
        method: "POST",
        data: { data: createOrderMarkupsModel.toSchema(data) },
        session,
      });

      return parseOrderMarkupsSchema(resp.json.data);
    } catch (err) {
      if (ensureJunctionError<{ data: CreateOrderSchema }>(err)) {
        const error = new z.ZodError<CreateOrderModel>([]);

        err.json?.errors.map(() => {
          throw error;
        });
      }

      throw err;
    }
  }

  async getOrder({ id, session }: { id: string; session: SessionModel }): Promise<OrderModel> {
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
      session,
    });

    const included = parseIncluded(resp.json.included);

    return parseOrderSchema(resp.json.data, included);
  }
}
