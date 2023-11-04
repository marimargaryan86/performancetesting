import integrationInstances from "integration-instances";
import { getSession } from "utils/auth";
import type { RequestEvent } from "./$types";
import { error } from "@sveltejs/kit";
import * as devalue from "devalue";
import { getPagination } from "../../helpers.server";
import type JourneyService from "integration/junction-hub-api/services/journey-service";

function find(event: RequestEvent): ReturnType<JourneyService["find"]> {
  const session = getSession(event);
  const pagination = getPagination(event);

  return integrationInstances.junctionHubApi.journeys.find({ session, ...pagination });
}

export async function GET(event): Promise<Response> {
  const method = event.url.searchParams.get("action")?.toString() as keyof JourneyService;

  switch (method) {
    case "find":
      return new Response(devalue.stringify(await find(event)));
    default:
      throw error(405);
  }
}
