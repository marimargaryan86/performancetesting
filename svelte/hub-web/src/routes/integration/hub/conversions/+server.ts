import integrationInstances from "integration-instances";
import { getSession } from "utils/auth";
import type { RequestEvent } from "./$types";
import { error } from "@sveltejs/kit";
import * as devalue from "devalue";
import type ConversionService from "integration/junction-hub-api/services/conversion-service";
import { getPagination } from "../../helpers.server";

function find(event: RequestEvent): ReturnType<ConversionService["find"]> {
  const session = getSession(event);
  const pagination = getPagination(event);

  return integrationInstances.junctionHubApi.conversions.find({ session, ...pagination });
}

function get(event: RequestEvent): ReturnType<ConversionService["get"]> {
  const session = getSession(event);
  const id = event.url.searchParams.get("id")?.toString();

  if (!id) {
    throw error(404);
  }

  try {
    return integrationInstances.junctionHubApi.conversions.get({ session, id });
  } catch {
    throw error(404);
  }
}

export async function GET(event): Promise<Response> {
  const method = event.url.searchParams.get("action")?.toString() as keyof ConversionService;

  switch (method) {
    case "find":
      return new Response(devalue.stringify(await find(event)));
    case "get":
      return new Response(devalue.stringify(await get(event)));
    default:
      throw error(405);
  }
}
