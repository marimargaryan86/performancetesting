import integrationInstances from "integration-instances";
import { getSession } from "utils/auth";
import type { RequestEvent } from "./$types";
import { error } from "@sveltejs/kit";
import * as devalue from "devalue";
import { getPagination } from "../../helpers.server";
import type TransactionService from "integration/junction-hub-api/services/transaction-service";

function find(event: RequestEvent): ReturnType<TransactionService["find"]> {
  const session = getSession(event);
  const pagination = getPagination(event);
  const sort = event.url.searchParams.get("sort")?.toString() as Parameters<
    TransactionService["find"]
  >[0]["sort"];
  const ids = event.url.searchParams.get("ids")?.toString().split(",");
  const billIds = event.url.searchParams.get("billIds")?.toString().split(",");
  const externalReference = event.url.searchParams.get("externalReference")?.toString();

  return integrationInstances.junctionHubApi.transactions.find({
    session,
    ...pagination,
    sort,
    filter: { ids, billIds, externalReference },
  });
}

function get(event: RequestEvent): ReturnType<TransactionService["get"]> {
  const session = getSession(event);
  const id = event.url.searchParams.get("id")?.toString();

  if (!id) {
    throw error(404);
  }

  try {
    return integrationInstances.junctionHubApi.transactions.get({ session, id });
  } catch {
    throw error(404);
  }
}

export async function GET(event): Promise<Response> {
  const method = event.url.searchParams.get("action")?.toString() as keyof TransactionService;

  switch (method) {
    case "find":
      return new Response(devalue.stringify(await find(event)));
    case "get":
      return new Response(devalue.stringify(await get(event)));
    default:
      throw error(405);
  }
}
