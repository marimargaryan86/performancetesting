import type RefundService from "integration/junction-hub-api/services/refund-service";
import * as devalue from "devalue";
import type { RequestEvent } from "./$types";
import type { PaginatedData } from "models/common";
import type { Refund, RefundPut } from "integration/junction-hub-api/schemas/refund";
import { getSession } from "utils/auth";
import { getPagination } from "../../helpers.server";
import integrationInstances from "integration-instances";
import { error } from "@sveltejs/kit";

function find(event: RequestEvent): Promise<PaginatedData<Refund>> {
  const session = getSession(event);
  const pagination = getPagination(event);

  return integrationInstances.junctionHubApi.refunds.find({ session, ...pagination });
}

function get(event: RequestEvent): Promise<Refund> {
  const session = getSession(event);
  const id = event.url.searchParams.get("id")?.toString();

  if (!id) {
    throw error(404);
  }

  return integrationInstances.junctionHubApi.refunds.get({ session, id });
}

async function create(event: RequestEvent): Promise<Refund> {
  const session = getSession(event);
  const data: RefundPut = devalue.parse(await event.request.text());

  return integrationInstances.junctionHubApi.refunds.create({ session, data });
}

async function update(event: RequestEvent): Promise<Refund> {
  const session = getSession(event);
  const id = event.url.searchParams.get("id")?.toString();

  if (!id) {
    throw error(404);
  }

  const data: RefundPut = devalue.parse(await event.request.text());

  return integrationInstances.junctionHubApi.refunds.update({ session, data, id });
}

export async function GET(event): Promise<Response> {
  const method = event.url.searchParams.get("action")?.toString() as keyof RefundService;

  switch (method) {
    case "find":
      return new Response(devalue.stringify(await find(event)));
    case "get":
      return new Response(devalue.stringify(await get(event)));
    default:
      throw error(405);
  }
}

export async function POST(event): Promise<Response> {
  const method = event.url.searchParams.get("action")?.toString() as keyof RefundService;

  switch (method) {
    case "create":
      return new Response(devalue.stringify(await create(event)));
    case "update":
      return new Response(devalue.stringify(await update(event)));
    default:
      throw error(405);
  }
}
