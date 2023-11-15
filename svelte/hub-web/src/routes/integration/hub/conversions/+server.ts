import integrationInstances from "integration-instances";
import type { RequestEvent } from "./$types";
import { error } from "@sveltejs/kit";
import * as devalue from "devalue";
import type ConversionService from "integration/junction-hub-api/services/conversion-service";
import { getPagination } from "../../helpers.server";
import { ensureJunctionError } from "integration/common/junction-error";

function find(event: RequestEvent): ReturnType<ConversionService["find"]> {
  const session = event.locals.session;
  const pagination = getPagination(event);

  return integrationInstances.junctionHubApi.conversions.find({ session, ...pagination });
}

function get(event: RequestEvent): ReturnType<ConversionService["get"]> {
  const session = event.locals.session;
  const id = event.url.searchParams.get("id")?.toString();

  if (!id) {
    throw error(404);
  }

  return integrationInstances.junctionHubApi.conversions.get({ session, id });
}

export async function GET(event): Promise<Response> {
  try {
    const method = event.url.searchParams.get("action")?.toString() as keyof ConversionService;

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
