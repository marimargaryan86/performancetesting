import integrationInstances from "integration-instances";
import { getSession } from "utils/auth";
import type { RequestEvent } from "./$types";
import { error } from "@sveltejs/kit";
import * as devalue from "devalue";
import type CancellationRequestService from "integration/junction-hub-api/services/cancellation-request-service";
import type { CancellationRequestCreate } from "integration/junction-hub-api/schemas/cancellation";

async function create(event: RequestEvent): ReturnType<CancellationRequestService["create"]> {
  const session = getSession(event);
  const data: CancellationRequestCreate = devalue.parse(await event.request.text());

  return integrationInstances.junctionHubApi.cancellationRequests.create({ session, data });
}

export async function POST(event): Promise<Response> {
  const method = event.url.searchParams
    .get("action")
    ?.toString() as keyof CancellationRequestService;

  switch (method) {
    case "create":
      return new Response(devalue.stringify(await create(event)));
    default:
      throw error(405);
  }
}
