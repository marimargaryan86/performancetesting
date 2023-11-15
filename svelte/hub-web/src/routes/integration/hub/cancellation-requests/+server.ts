import integrationInstances from "integration-instances";
import { getSession } from "utils/auth";
import type { RequestEvent } from "./$types";
import { error } from "@sveltejs/kit";
import * as devalue from "devalue";
import type CancellationRequestService from "integration/junction-hub-api/services/cancellation-request-service";
import type { CancellationRequestCreate } from "integration/junction-hub-api/schemas/cancellation";
import { ensureJunctionError } from "integration/common/junction-error";

async function create(event: RequestEvent): ReturnType<CancellationRequestService["create"]> {
  const session = getSession(event);
  const data: CancellationRequestCreate = devalue.parse(await event.request.text());

  return integrationInstances.junctionHubApi.cancellationRequests.create({ session, data });
}

export async function POST(event): Promise<Response> {
  try {
    const method = event.url.searchParams
      .get("action")
      ?.toString() as keyof CancellationRequestService;

    switch (method) {
      case "create":
        return new Response(devalue.stringify(await create(event)));
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
