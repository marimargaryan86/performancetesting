import integrationInstances from "integration-instances";
import { getSession } from "utils/auth";
import type { RequestEvent } from "./$types";
import { error } from "@sveltejs/kit";
import * as devalue from "devalue";
import type PlaceService from "integration/junction-mobile-api/services/place-service";

function find(event: RequestEvent): ReturnType<PlaceService["find"]> {
  const session = getSession(event);
  const query = event.url.searchParams.get("query")?.toString();

  return integrationInstances.junctionMobileApi.places.find({ session, query: query ?? "" });
}

function get(event: RequestEvent): ReturnType<PlaceService["get"]> {
  const session = getSession(event);
  const id = event.url.searchParams.get("id")?.toString();

  if (!id) {
    throw error(404);
  }

  try {
    return integrationInstances.junctionMobileApi.places.get({ session, id });
  } catch {
    throw error(404);
  }
}

export async function GET(event): Promise<Response> {
  const method = event.url.searchParams.get("action")?.toString() as keyof PlaceService;

  switch (method) {
    case "find":
      return new Response(devalue.stringify(await find(event)));
    case "get":
      return new Response(devalue.stringify(await get(event)));
    default:
      throw error(405);
  }
}
