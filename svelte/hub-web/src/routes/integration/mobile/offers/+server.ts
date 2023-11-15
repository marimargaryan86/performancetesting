import integrationInstances from "integration-instances";
import type { RequestEvent } from "./$types";
import { error } from "@sveltejs/kit";
import * as devalue from "devalue";
import type OfferService from "integration/junction-mobile-api/services/offer-service";
import type { TripOfferPriceQuoteCreate } from "integration/junction-mobile-api/schemas/trip-offer-price-quote";
import { ensureJunctionError } from "integration/common/junction-error";

async function create(event: RequestEvent): ReturnType<OfferService["create"]> {
  const session = event.locals.session;
  const data: TripOfferPriceQuoteCreate = devalue.parse(await event.request.text());

  return integrationInstances.junctionMobileApi.offers.create({ session, data });
}

function get(event: RequestEvent): ReturnType<OfferService["get"]> {
  const session = event.locals.session;
  const id = event.url.searchParams.get("id")?.toString();

  if (!id) {
    throw error(404);
  }

  return integrationInstances.junctionMobileApi.offers.get({ session, id });
}

export async function GET(event): Promise<Response> {
  try {
    const method = event.url.searchParams.get("action")?.toString() as keyof OfferService;

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

export async function POST(event): Promise<Response> {
  try {
    const method = event.url.searchParams.get("action")?.toString() as keyof OfferService;

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
