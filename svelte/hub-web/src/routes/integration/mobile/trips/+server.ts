import integrationInstances from "integration-instances";
import { getSession } from "utils/auth";
import type { RequestEvent } from "./$types";
import { error } from "@sveltejs/kit";
import * as devalue from "devalue";
import type TripService from "integration/junction-mobile-api/services/trip-service";
import type { TripCandidateSearchCreate } from "integration/junction-mobile-api/schemas/trip-candidate";
import { getPagination } from "../../helpers.server";
import { ensureJunctionError } from "integration/common/junction-error";

async function create(event: RequestEvent): ReturnType<TripService["create"]> {
  const session = getSession(event);
  const data: TripCandidateSearchCreate = devalue.parse(await event.request.text());

  return integrationInstances.junctionMobileApi.trips.create({ session, data });
}

function getTripCandidateSearch(
  event: RequestEvent,
): ReturnType<TripService["getTripCandidateSearch"]> {
  const session = getSession(event);
  const id = event.url.searchParams.get("id")?.toString();

  if (!id) {
    throw error(404);
  }

  return integrationInstances.junctionMobileApi.trips.getTripCandidateSearch({ session, id });
}

function findOffers(event: RequestEvent): ReturnType<TripService["findOffers"]> {
  const session = getSession(event);
  const id = event.url.searchParams.get("id")?.toString();

  if (!id) {
    throw error(404);
  }

  const pagination = getPagination(event);

  return integrationInstances.junctionMobileApi.trips.findOffers({ session, id, ...pagination });
}

export async function GET(event): Promise<Response> {
  try {
    const method = event.url.searchParams.get("action")?.toString() as keyof TripService;

    switch (method) {
      case "findOffers":
        return new Response(devalue.stringify(await findOffers(event)));
      case "getTripCandidateSearch":
        return new Response(devalue.stringify(await getTripCandidateSearch(event)));
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

export async function POST(event): Promise<Response> {
  try {
    const method = event.url.searchParams.get("action")?.toString() as keyof TripService;

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
