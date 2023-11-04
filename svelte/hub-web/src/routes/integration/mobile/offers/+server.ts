import integrationInstances from "integration-instances";
import { getSession } from "utils/auth";
import type { RequestEvent } from "./$types";
import { error } from "@sveltejs/kit";
import * as devalue from "devalue";
import type OfferService from "integration/junction-mobile-api/services/offer-service";
import type { TripOfferPriceQuoteCreate } from "integration/junction-mobile-api/schemas/trip-offer-price-quote";

async function create(event: RequestEvent): ReturnType<OfferService["create"]> {
  const session = getSession(event);
  const data: TripOfferPriceQuoteCreate = devalue.parse(await event.request.text());

  return integrationInstances.junctionMobileApi.offers.create({ session, data });
}

function get(event: RequestEvent): ReturnType<OfferService["get"]> {
  const session = getSession(event);
  const id = event.url.searchParams.get("id")?.toString();

  if (!id) {
    throw error(404);
  }

  try {
    return integrationInstances.junctionMobileApi.offers.get({ session, id });
  } catch {
    throw error(404);
  }
}

export async function GET(event): Promise<Response> {
  const method = event.url.searchParams.get("action")?.toString() as keyof OfferService;

  switch (method) {
    case "get":
      return new Response(devalue.stringify(await get(event)));
    default:
      throw error(405);
  }
}

export async function POST(event): Promise<Response> {
  const method = event.url.searchParams.get("action")?.toString() as keyof OfferService;

  switch (method) {
    case "create":
      return new Response(devalue.stringify(await create(event)));
    default:
      throw error(405);
  }
}
