import * as devalue from "devalue";
import {
  coordinatesSearchableModel,
  type PlaceModel,
} from "integration/junction-mobile-api/schemas/place";
import type { RouteId } from "./$types";
import { URLExtended } from "utils/url";
import { z } from "zod";
import { passengerPickerData } from "../../trip-management/components/trip-search/passenger-picker/passenger-picker.svelte";
import type {
  OfferModel,
  TripOfferPriceQuoteModel,
} from "integration/junction-mobile-api/schemas/offer";
import type { RequestEvent } from "@sveltejs/kit";
import {
  resourceStatus,
  type ResourceStatus,
} from "integration/junction-mobile-api/schemas/common";
import { sleep } from "utils/common";
import { priceModel } from "integration/junction-mobile-api/schemas/price";
import {
  paymentIntentModel,
  type PaymentIntentModel,
} from "integration/junction-mobile-api/schemas/payment";
import type { CreateOrderModel, OrderModel } from "integration/junction-mobile-api/schemas/order";

const ROUTE: RouteId = "/integration/trip-management";

const point = coordinatesSearchableModel.model.extend({
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
      originalPrice: priceModel.model,
    }),
    offers: z.object({
      expiresAt: z.date().optional(),
    }),
    priceQuote: z.object({
      id: z.string(),
      status: resourceStatus,
      expiresAt: z.date(),
    }),
    paymentIntent: paymentIntentModel.model.extend({ confirmed: z.boolean().optional() }),
    order: z.object({
      id: z.string(),
    }),
  })
  .partial();
export type BookingSessionModel = z.infer<typeof bookingSessionModel>;

async function listPlaces(query: string): Promise<PlaceModel[]> {
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

async function getOffers(
  event?: RequestEvent,
): Promise<{ data: OfferModel[]; status: ResourceStatus }> {
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
): AsyncGenerator<OfferModel> {
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

function yieldOffers(signal: { cancelled: boolean }): AsyncGenerator<OfferModel> {
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

async function getPriceQuote(): Promise<TripOfferPriceQuoteModel> {
  const url = new URLExtended(ROUTE, { base: origin, query: { action: "get-price-quote" } });
  const resp = await fetch(url);

  if (resp.status !== 200) {
    throw new Error("Failed to get price quote");
  }

  return devalue.parse(await resp.text());
}

async function getPaymentIntent(): Promise<PaymentIntentModel> {
  const url = new URLExtended(ROUTE, { base: origin, query: { action: "get-payment-intent" } });
  const resp = await fetch(url);

  if (resp.status !== 200) {
    throw new Error("Failed to get payment intent");
  }

  return devalue.parse(await resp.text());
}

async function createOrder(
  data: CreateOrderModel,
): Promise<
  { success: true; order: OrderModel } | { success: false; errors: z.ZodFormattedError<unknown> }
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

async function createOrderMarkups(): Promise<void> {
  // TODO: Implement

  await sleep(1000);
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
