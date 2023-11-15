import integrationInstances from "integration-instances";
import { getSession } from "utils/auth";
import type { RequestEvent } from "./$types";
import { error } from "@sveltejs/kit";
import * as devalue from "devalue";
import type OrderService from "integration/junction-mobile-api/services/order-service";
import type { OrderCreate } from "integration/junction-mobile-api/schemas/order";
import { getPagination } from "../../helpers.server";
import type { MarkupsCreate } from "integration/junction-mobile-api/schemas/markups";
import { ensureJunctionError } from "integration/common/junction-error";

async function create(event: RequestEvent): ReturnType<OrderService["create"]> {
  const session = getSession(event);
  const data: OrderCreate = devalue.parse(await event.request.text());

  return integrationInstances.junctionMobileApi.orders.create({ session, data });
}

async function createMarkups(event: RequestEvent): ReturnType<OrderService["createMarkups"]> {
  const session = getSession(event);
  const data: MarkupsCreate = devalue.parse(await event.request.text());

  return integrationInstances.junctionMobileApi.orders.createMarkups({ session, data });
}

function find(event: RequestEvent): ReturnType<OrderService["find"]> {
  const session = getSession(event);
  const pagination = getPagination(event);

  return integrationInstances.junctionMobileApi.orders.find({ session, ...pagination });
}

function get(event: RequestEvent): ReturnType<OrderService["get"]> {
  const session = getSession(event);
  const id = event.url.searchParams.get("id")?.toString();

  if (!id) {
    throw error(404);
  }

  return integrationInstances.junctionMobileApi.orders.get({ session, id });
}

function getMarkups(event: RequestEvent): ReturnType<OrderService["getMarkups"]> {
  const session = getSession(event);
  const orderId = event.url.searchParams.get("orderId")?.toString();

  if (!orderId) {
    throw error(404);
  }

  return integrationInstances.junctionMobileApi.orders.getMarkups({ session, orderId });
}

export async function GET(event): Promise<Response> {
  try {
    const method = event.url.searchParams.get("action")?.toString() as keyof OrderService;

    switch (method) {
      case "find":
        return new Response(devalue.stringify(await find(event)));
      case "get":
        return new Response(devalue.stringify(await get(event)));
      case "getMarkups":
        return new Response(devalue.stringify(await getMarkups(event)));
      default:
        throw new Error("An unexpected error occured");
    }
  } catch (err) {
    if (ensureJunctionError(err)) {
      throw error(err.status, { message: err.message });
    }

    throw error(500);
  }
}

export async function POST(event): Promise<Response> {
  try {
    const method = event.url.searchParams.get("action")?.toString() as keyof OrderService;

    switch (method) {
      case "create":
        return new Response(devalue.stringify(await create(event)));
      case "createMarkups":
        return new Response(devalue.stringify(await createMarkups(event)));
      default:
        throw new Error("An unexpected error occured");
    }
  } catch (err) {
    if (ensureJunctionError(err)) {
      throw error(err.status, { message: err.message });
    }

    throw error(500);
  }
}
