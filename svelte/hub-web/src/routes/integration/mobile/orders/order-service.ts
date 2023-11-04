import { URLExtended } from "utils/url";
import * as devalue from "devalue";
import { MOBILE_INTEGRATION_ROOT } from "../common";
import type OrderService from "integration/junction-mobile-api/services/order-service";
import type { OrderCreate } from "integration/junction-mobile-api/schemas/order";
import type { MarkupsCreate } from "integration/junction-mobile-api/schemas/markups";

const ROOT = `${MOBILE_INTEGRATION_ROOT}/orders`;

async function create({ data }: { data: OrderCreate }): ReturnType<OrderService["create"]> {
  const url = new URLExtended(ROOT, {
    base: origin,
    query: { action: "create" },
  });
  const resp = await fetch(url, { method: "POST", body: devalue.stringify(data) });

  return devalue.parse(await resp.text());
}

async function find({
  cursor,
  limit,
}: {
  cursor?: string;
  limit?: number;
}): ReturnType<OrderService["find"]> {
  const url = new URLExtended(ROOT, { base: origin, query: { cursor, limit, action: "find" } });
  const resp = await fetch(url);

  return devalue.parse(await resp.text());
}

async function get({ id }: { id: string }): ReturnType<OrderService["get"]> {
  const url = new URLExtended(ROOT, { base: origin, query: { id, action: "get" } });
  const resp = await fetch(url);

  if (resp.status !== 200) {
    throw new Error("Order not found");
  }

  return devalue.parse(await resp.text());
}

async function getMarkups({
  orderId,
}: {
  orderId: string;
}): ReturnType<OrderService["getMarkups"]> {
  const url = new URLExtended(ROOT, { base: origin, query: { orderId, action: "getMarkups" } });
  const resp = await fetch(url);

  if (resp.status !== 200) {
    throw new Error("Markups not found");
  }

  return devalue.parse(await resp.text());
}

async function createMarkups({
  data,
}: {
  data: MarkupsCreate;
}): ReturnType<OrderService["createMarkups"]> {
  const url = new URLExtended(ROOT, { base: origin, query: { action: "createMarkups" } });
  const resp = await fetch(url, { method: "POST", body: devalue.stringify(data) });

  if (resp.status !== 200) {
    throw new Error("Markups not found");
  }

  return devalue.parse(await resp.text());
}

export default {
  create,
  find,
  get,
  getMarkups,
  createMarkups,
};
