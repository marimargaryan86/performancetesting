import integrationInstances from "integration-instances";
import type { RequestEvent } from "./$types";
import { error } from "@sveltejs/kit";
import * as devalue from "devalue";
import { getPagination } from "../../helpers.server";
import type JourneyService from "integration/junction-hub-api/services/journey-service";
import { ensureJunctionError } from "integration/common/junction-error";

function find(event: RequestEvent): ReturnType<JourneyService["find"]> {
  const session = event.locals.session;
  const pagination = getPagination(event);
  const sort = event.url.searchParams.get("sort")?.toString() as Parameters<
    JourneyService["find"]
  >[0]["sort"];

  return integrationInstances.junctionHubApi.journeys.find({ session, ...pagination, sort });
}

export async function GET(event): Promise<Response> {
  try {
    const method = event.url.searchParams.get("action")?.toString() as keyof JourneyService;

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
