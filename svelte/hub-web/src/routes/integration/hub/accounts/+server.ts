import integrationInstances from "integration-instances";
import type AccountService from "integration/junction-hub-api/services/account-service";
import type { RequestEvent } from "./$types";
import { error } from "@sveltejs/kit";
import * as devalue from "devalue";
import { getPagination } from "../../helpers.server";
import { ensureJunctionError } from "integration/common/junction-error";

function find(event: RequestEvent): ReturnType<AccountService["find"]> {
  const session = event.locals.session;
  const pagination = getPagination(event);

  return integrationInstances.junctionHubApi.accounts.find({ session, ...pagination });
}

function get(event: RequestEvent): ReturnType<AccountService["get"]> {
  const session = event.locals.session;
  const id = event.url.searchParams.get("id")?.toString();

  if (!id) {
    throw error(404);
  }

  return integrationInstances.junctionHubApi.accounts.get({ session, id });
}

export async function GET(event): Promise<Response> {
  try {
    const method = event.url.searchParams.get("action")?.toString() as keyof AccountService;

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
