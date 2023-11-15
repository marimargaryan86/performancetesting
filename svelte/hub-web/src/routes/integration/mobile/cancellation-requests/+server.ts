import integrationInstances from "integration-instances";
import { getSession } from "utils/auth";
import type { RequestEvent } from "./$types";
import { error } from "@sveltejs/kit";
import * as devalue from "devalue";
import type CancellationRequestService from "integration/junction-mobile-api/services/cancellation-request-service";
import type { CancellationRequestCreate } from "integration/junction-mobile-api/schemas/cancellation";
import { ensureJunctionError } from "integration/common/junction-error";

async function create(event: RequestEvent): ReturnType<CancellationRequestService["create"]> {
  const session = getSession(event);
  const data: CancellationRequestCreate = devalue.parse(await event.request.text());

  return integrationInstances.junctionMobileApi.cancellations.create({ session, data });
}

function get(event: RequestEvent): ReturnType<CancellationRequestService["get"]> {
  const session = getSession(event);
  const id = event.url.searchParams.get("id")?.toString();

  if (!id) {
    throw error(404);
  }

  return integrationInstances.junctionMobileApi.cancellations.get({ session, id });
}

export async function GET(event): Promise<Response> {
  const method = event.url.searchParams
    .get("action")
    ?.toString() as keyof CancellationRequestService;

  switch (method) {
    case "get":
      return new Response(devalue.stringify(await get(event)));
    default:
      throw error(405);
  }
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
