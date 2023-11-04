import integrationInstances from "integration-instances";
import { getSession } from "utils/auth";
import type { RequestEvent } from "./$types";
import { error } from "@sveltejs/kit";
import * as devalue from "devalue";
import { getPagination } from "../../helpers.server";
import type BalanceService from "integration/junction-hub-api/services/balance-service";
import type { BalanceAdd } from "integration/junction-hub-api/schemas/balance";

function find(event: RequestEvent): ReturnType<BalanceService["find"]> {
  const session = getSession(event);
  const accountId = event.url.searchParams.get("accountId")?.toString();

  if (!accountId) {
    throw error(404);
  }

  const pagination = getPagination(event);

  try {
    return integrationInstances.junctionHubApi.balances.find({
      session,
      accountId,
      ...pagination,
    });
  } catch {
    throw error(404);
  }
}

async function create(event: RequestEvent): ReturnType<BalanceService["create"]> {
  const session = getSession(event);
  const accountId = event.url.searchParams.get("accountId")?.toString();

  if (!accountId) {
    throw error(404);
  }

  const data: BalanceAdd = devalue.parse(await event.request.text());

  try {
    return integrationInstances.junctionHubApi.balances.create({ session, accountId, data });
  } catch {
    throw error(404);
  }
}

export async function GET(event): Promise<Response> {
  const method = event.url.searchParams.get("action")?.toString() as keyof BalanceService;

  switch (method) {
    case "find":
      return new Response(devalue.stringify(await find(event)));
    default:
      throw error(405);
  }
}

export async function POST(event): Promise<Response> {
  const method = event.url.searchParams.get("action")?.toString() as keyof BalanceService;

  switch (method) {
    case "create":
      return new Response(devalue.stringify(await create(event)));
    default:
      throw error(405);
  }
}
