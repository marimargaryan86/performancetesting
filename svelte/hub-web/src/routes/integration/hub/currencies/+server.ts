import integrationInstances from "integration-instances";
import { getSession } from "utils/auth";
import type { RequestEvent } from "./$types";
import { error } from "@sveltejs/kit";
import * as devalue from "devalue";
import type CurrencyService from "integration/junction-hub-api/services/currency-service";
import { getPagination } from "../../helpers.server";
import { ensureJunctionError } from "integration/common/junction-error";

function find(event: RequestEvent): ReturnType<CurrencyService["find"]> {
  const session = getSession(event);
  const pagination = getPagination(event);

  return integrationInstances.junctionHubApi.currencies.find({ session, ...pagination });
}

export async function GET(event): Promise<Response> {
  try {
    const method = event.url.searchParams.get("action")?.toString() as keyof CurrencyService;

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
