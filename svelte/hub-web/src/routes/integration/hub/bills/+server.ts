import integrationInstances from "integration-instances";
import { getSession } from "utils/auth";
import type { RequestEvent } from "./$types";
import { error } from "@sveltejs/kit";
import * as devalue from "devalue";
import { getPagination } from "../../helpers.server";
import type BillService from "integration/junction-hub-api/services/bill-service";
import type { Bill } from "integration/junction-hub-api/schemas/bill";

function find(event: RequestEvent): ReturnType<BillService["find"]> {
  const session = getSession(event);
  const pagination = getPagination(event);

  return integrationInstances.junctionHubApi.bills.find({
    session,
    ...pagination,
  });
}

function get(event: RequestEvent): ReturnType<BillService["get"]> {
  const session = getSession(event);
  const id = event.url.searchParams.get("id")?.toString();

  if (!id) {
    throw error(404);
  }

  try {
    return integrationInstances.junctionHubApi.bills.get({ session, id });
  } catch {
    throw error(404);
  }
}

async function toggleReconciliation(
  event: RequestEvent,
): ReturnType<BillService["toggleReconciliation"]> {
  const session = getSession(event);
  const data: Bill = devalue.parse(await event.request.text());

  return integrationInstances.junctionHubApi.bills.toggleReconciliation({ session, bill: data });
}

export async function GET(event): Promise<Response> {
  const method = event.url.searchParams.get("action")?.toString() as keyof BillService;

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
  const method = event.url.searchParams.get("action")?.toString() as keyof BillService;

  switch (method) {
    case "toggleReconciliation":
      return new Response(devalue.stringify(await toggleReconciliation(event)));
    default:
      throw error(405);
  }
}
