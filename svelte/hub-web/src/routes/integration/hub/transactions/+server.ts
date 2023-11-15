import integrationInstances from "integration-instances";
import type { RequestEvent } from "./$types";
import { error } from "@sveltejs/kit";
import * as devalue from "devalue";
import { getPagination } from "../../helpers.server";
import type TransactionService from "integration/junction-hub-api/services/transaction-service";
import { ensureJunctionError } from "integration/common/junction-error";

function find(event: RequestEvent): ReturnType<TransactionService["find"]> {
  const session = event.locals.session;
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
  const session = event.locals.session;
  const id = event.url.searchParams.get("id")?.toString();

  if (!id) {
    throw error(404);
  }

  return integrationInstances.junctionHubApi.transactions.get({ session, id });
}

export async function GET(event): Promise<Response> {
  try {
    const method = event.url.searchParams.get("action")?.toString() as keyof TransactionService;

    switch (method) {
      case "find":
        return new Response(devalue.stringify(await find(event)));
      case "get":
        return new Response(devalue.stringify(await get(event)));
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
