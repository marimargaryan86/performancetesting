import integrationInstances from "integration-instances";
import type { RequestEvent } from "./$types";
import { error } from "@sveltejs/kit";
import * as devalue from "devalue";
import { getPagination } from "../../helpers.server";
import type BalanceService from "integration/junction-hub-api/services/balance-service";
import type { BalanceAdd } from "integration/junction-hub-api/schemas/balance";
import { ensureJunctionError } from "integration/common/junction-error";

function find(event: RequestEvent): ReturnType<BalanceService["find"]> {
  const session = event.locals.session;
  const accountId = event.url.searchParams.get("accountId")?.toString();

  if (!accountId) {
    throw error(404);
  }

  const pagination = getPagination(event);

  return integrationInstances.junctionHubApi.balances.find({ session, accountId, ...pagination });
}

async function create(event: RequestEvent): ReturnType<BalanceService["create"]> {
  const session = event.locals.session;
  const accountId = event.url.searchParams.get("accountId")?.toString();

  if (!accountId) {
    throw error(404);
  }

  const data: BalanceAdd = devalue.parse(await event.request.text());

  return integrationInstances.junctionHubApi.balances.create({ session, accountId, data });
}

export async function GET(event): Promise<Response> {
  try {
    const method = event.url.searchParams.get("action")?.toString() as keyof BalanceService;

    switch (method) {
      case "find":
        return new Response(devalue.stringify(await find(event)));
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
    const method = event.url.searchParams.get("action")?.toString() as keyof BalanceService;

    switch (method) {
      case "create":
        return new Response(devalue.stringify(await create(event)));
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
