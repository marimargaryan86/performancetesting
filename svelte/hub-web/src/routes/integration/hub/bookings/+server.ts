import integrationInstances from "integration-instances";
import type { RequestEvent } from "./$types";
import { error } from "@sveltejs/kit";
import * as devalue from "devalue";
import type BookingService from "integration/junction-hub-api/services/booking-service";
import { ensureJunctionError } from "integration/common/junction-error";

function get(event: RequestEvent): ReturnType<BookingService["get"]> {
  const session = event.locals.session;
  const id = event.url.searchParams.get("id")?.toString();

  if (!id) {
    throw error(404);
  }

  return integrationInstances.junctionHubApi.bookings.get({ session, id });
}

export async function GET(event): Promise<Response> {
  try {
    const method = event.url.searchParams.get("action")?.toString() as keyof BookingService;

    switch (method) {
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
