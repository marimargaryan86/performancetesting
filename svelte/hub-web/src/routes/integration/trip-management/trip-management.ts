import * as devalue from "devalue";
import type { Place } from "integration/junction-mobile-api/schemas/place";
import type { RouteId } from "./$types";
import { URLExtended } from "utils/url";
import { z } from "zod";
import { passengerPickerData } from "../../trip-management/components/trip-search/passenger-picker/passenger-picker.svelte";
import type { Offer } from "integration/junction-mobile-api/schemas/offer";
import type { RequestEvent } from "@sveltejs/kit";
import { sleep } from "utils/common";
import { paymentModel, type Payment } from "integration/junction-mobile-api/schemas/payment";
import type { OrderCreate, Order } from "integration/junction-mobile-api/schemas/order";
import type { TripOfferPriceQuote } from "integration/junction-mobile-api/schemas/trip-offer-price-quote";
import type { MarkupsCreate } from "integration/junction-mobile-api/schemas/markups";
import { priceModel } from "integration/common/schemas/price";
import { resourceStatus, type ResourceStatus } from "integration/common/schemas/resource";
import { coordinatesSearchableModel } from "integration/common/schemas/point";

const ROUTE: RouteId = "/integration/trip-management";

const point = coordinatesSearchableModel.extend({
  id: z.string(),
});

export const searchDataModel = z.object({
  origin: z.object(point.shape, { required_error: "Origin is mandatory" }),
  destination: z.object(point.shape, { required_error: "Destination is mandatory" }),
  outbound: z.date({ coerce: true, required_error: "Departure date is mandatory" }),
  passengers: passengerPickerData,
});
export type SearchDataModel = z.infer<typeof searchDataModel>;

export const bookingSessionModel = z
  .object({
    sessionToken: z.string(),
    searchData: searchDataModel,
    tripCandidates: z.object({
      id: z.string(),
      expiresAt: z.date(),
      status: resourceStatus,
    }),
    selected: z.object({
      offerId: z.string(),
      optionIds: z.array(z.string()).min(1),
      originalPrice: priceModel,
    }),
    offers: z.object({
      expiresAt: z.date().optional(),
    }),
    priceQuote: z.object({
      id: z.string(),
      status: resourceStatus,
      expiresAt: z.date(),
    }),
    paymentIntent: paymentModel.extend({ confirmed: z.boolean().optional() }),
    order: z.object({
      id: z.string(),
    }),
    orderMarkups: z.object({
      id: z.string(),
    }),
  })
  .partial();
export type BookingSessionModel = z.infer<typeof bookingSessionModel>;

async function listPlaces(query: string): Promise<Place[]> {
  if (query.length < 3) {
    return [];
  }

  const url = new URLExtended(ROUTE, { base: origin, query: { action: "list-places", query } });
  const resp = await fetch(url);

  if (resp.status !== 200) {
    throw new Error("Failed to fetch places");
  }

  return devalue.parse(await resp.text());
}

async function search(data: Partial<SearchDataModel>): Promise<void> {
  const parsed = searchDataModel.parse(data);
  const url = new URLExtended(ROUTE, { base: origin, query: { action: "search" } });
  const resp = await fetch(url, { method: "POST", body: devalue.stringify(parsed) });

  if (resp.status !== 204) {
    throw new Error("Failed to search");
  }
}

async function getOffers(event?: RequestEvent): Promise<{ data: Offer[]; status: ResourceStatus }> {
  const url = new URLExtended(ROUTE, {
    base: event?.url.origin ?? origin,
    query: { action: "get-offers" },
  });
  const resp = await (event?.fetch ?? fetch)(url);

  if (resp.status !== 200) {
    throw new Error("Failed to get offers");
  }

  return devalue.parse(await resp.text());
}

async function* yieldOffersAux(
  signal: { cancelled: boolean },
  ids: string[] = [],
): AsyncGenerator<Offer> {
  const result = await getOffers();
  const offers = result.data.filter((item) => !ids.includes(item.id));
  const nextIds = [...ids, ...offers.map((item) => item.id)];

  for (const offer of offers) {
    yield offer;
  }

  if (result.status !== "completed" && !signal.cancelled) {
    await sleep(2000);

    for await (const offer of yieldOffersAux(signal, nextIds)) {
      yield offer;
    }
  }
}

function yieldOffers(signal: { cancelled: boolean }): AsyncGenerator<Offer> {
  return yieldOffersAux(signal);
}

async function selectOffer(
  selectedOffer: NonNullable<BookingSessionModel["selected"]>,
): Promise<void> {
  if (!selectedOffer.optionIds.length) {
    throw new Error("No option selected");
  }

  const url = new URLExtended(ROUTE, { base: origin, query: { action: "select-offer" } });
  const resp = await fetch(url, {
    method: "POST",
    body: devalue.stringify(selectedOffer),
  });

  if (resp.status !== 204) {
    throw new Error("Failed to select offer");
  }
}

async function getPriceQuote(): Promise<TripOfferPriceQuote> {
  const url = new URLExtended(ROUTE, { base: origin, query: { action: "get-price-quote" } });
  const resp = await fetch(url);

  if (resp.status !== 200) {
    throw new Error("Failed to get price quote");
  }

  return devalue.parse(await resp.text());
}

async function getPaymentIntent(): Promise<Payment> {
  const url = new URLExtended(ROUTE, { base: origin, query: { action: "get-payment-intent" } });
  const resp = await fetch(url);

  if (resp.status !== 200) {
    throw new Error("Failed to get payment intent");
  }

  return devalue.parse(await resp.text());
}

async function createOrder(
  data: OrderCreate,
): Promise<
  { success: true; order: Order } | { success: false; errors: z.ZodFormattedError<unknown> }
> {
  const url = new URLExtended(ROUTE, { base: origin, query: { action: "create-order" } });
  const resp = await fetch(url, { method: "POST", body: devalue.stringify(data) });

  if (resp.status === 422) {
    return { success: false, errors: devalue.parse(await resp.text()) };
  }

  if (resp.status !== 201) {
    throw new Error("Failed to create order");
  }

  return { success: true, order: devalue.parse(await resp.text()) };
}

async function confirmPayment(): Promise<void> {
  const url = new URLExtended(ROUTE, { base: origin, query: { action: "confirm-payment" } });
  const resp = await fetch(url, { method: "POST" });

  if (resp.status !== 200) {
    throw new Error("Failed to confirm payment");
  }
}

async function createOrderMarkups(
  data: MarkupsCreate,
): Promise<
  { success: true; order: MarkupsCreate } | { success: false; errors: z.ZodFormattedError<unknown> }
> {
  const url = new URLExtended(ROUTE, { base: origin, query: { action: "create-order-markups" } });
  const resp = await fetch(url, { method: "POST", body: devalue.stringify(data) });

  if (resp.status === 422) {
    return { success: false, errors: devalue.parse(await resp.text()) };
  }

  if (resp.status !== 201) {
    throw new Error("Failed to create order markups");
  }

  return { success: true, order: devalue.parse(await resp.text()) };
}

export default {
  listPlaces,
  search,
  getOffers,
  yieldOffers,
  selectOffer,
  getPriceQuote,
  getPaymentIntent,
  createOrder,
  confirmPayment,
  createOrderMarkups,
};
