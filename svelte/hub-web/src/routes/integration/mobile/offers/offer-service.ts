import { URLExtended } from "utils/url";
import * as devalue from "devalue";
import { MOBILE_INTEGRATION_ROOT } from "../common";
import type { TripOfferPriceQuoteCreate } from "integration/junction-mobile-api/schemas/trip-offer-price-quote";
import type OfferService from "integration/junction-mobile-api/services/offer-service";

const ROOT = `${MOBILE_INTEGRATION_ROOT}/offers`;

async function create({
  data,
}: {
  data: TripOfferPriceQuoteCreate;
}): ReturnType<OfferService["create"]> {
  const url = new URLExtended(ROOT, {
    base: origin,
    query: { action: "create" },
  });
  const resp = await fetch(url, { method: "POST", body: devalue.stringify(data) });

  return devalue.parse(await resp.text());
}

async function get({ id }: { id: string }): ReturnType<OfferService["get"]> {
  const url = new URLExtended(ROOT, { base: origin, query: { id, action: "get" } });
  const resp = await fetch(url);

  if (resp.status !== 200) {
    throw new Error("Offer price quote not found");
  }

  return devalue.parse(await resp.text());
}

export default {
  create,
  get,
};
