import integrationInstances from "integration-instances";
import type AccountService from "integration/junction-hub-api/services/account-service";
import { getSession } from "utils/auth";
import type { RequestEvent } from "./$types";
import { error } from "@sveltejs/kit";
import * as devalue from "devalue";
import { getPagination } from "../../helpers.server";

function find(event: RequestEvent): ReturnType<AccountService["find"]> {
  const session = getSession(event);
  const pagination = getPagination(event);

  return integrationInstances.junctionHubApi.accounts.find({
    session,
    ...pagination,
  });
}

function get(event: RequestEvent): ReturnType<AccountService["get"]> {
  const session = getSession(event);
  const id = event.url.searchParams.get("id")?.toString();

  if (!id) {
    throw error(404);
  }

  try {
    return integrationInstances.junctionHubApi.accounts.get({ session, id });
  } catch {
    throw error(404);
  }
}

export async function GET(event): Promise<Response> {
  const method = event.url.searchParams.get("action")?.toString() as keyof AccountService;

  switch (method) {
    case "find":
      return new Response(devalue.stringify(await find(event)));
    case "get":
      return new Response(devalue.stringify(await get(event)));
    default:
      throw error(405);
  }
}
