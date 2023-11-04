import integrationInstances from "integration-instances";
import { getSession } from "utils/auth";
import type { RequestEvent } from "./$types";
import { error } from "@sveltejs/kit";
import * as devalue from "devalue";
import type TripService from "integration/junction-mobile-api/services/trip-service";
import type { TripCandidateSearchCreate } from "integration/junction-mobile-api/schemas/trip-candidate";
import { getPagination } from "../../helpers.server";

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

  try {
    return integrationInstances.junctionMobileApi.trips.findOffers({ session, id, ...pagination });
  } catch {
    throw error(404);
  }
}

export async function GET(event): Promise<Response> {
  const method = event.url.searchParams.get("action")?.toString() as keyof TripService;

  switch (method) {
    case "findOffers":
      return new Response(devalue.stringify(await findOffers(event)));
    case "getTripCandidateSearch":
      return new Response(devalue.stringify(await getTripCandidateSearch(event)));
    default:
      throw error(405);
  }
}

export async function POST(event): Promise<Response> {
  const method = event.url.searchParams.get("action")?.toString() as keyof TripService;

  switch (method) {
    case "create":
      return new Response(devalue.stringify(await create(event)));
    default:
      throw error(405);
  }
}
