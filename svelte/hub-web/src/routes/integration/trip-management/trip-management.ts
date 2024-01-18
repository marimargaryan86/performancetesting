import type { RouteId } from "./$types";
import { z } from "zod";
import { passengerPickerData } from "../../trip-management/components/trip-search/passenger-picker/passenger-picker.svelte";
import type { Offer } from "integration/junction-mobile-api/schemas/offer";
import { sleep } from "utils/common";
import { paymentModel, type Payment } from "integration/junction-mobile-api/schemas/payment";
import type { OrderCreate, Order } from "integration/junction-mobile-api/schemas/order";
import type { TripOfferPriceQuote } from "integration/junction-mobile-api/schemas/trip-offer-price-quote";
import type { MarkupsCreate } from "integration/junction-mobile-api/schemas/markups";
import { priceModel } from "integration/common/schemas/price";
import { resourceStatus, type ResourceStatus } from "integration/common/schemas/resource";
import { coordinatesSearchableModel } from "integration/common/schemas/point";
import { clientServiceFactory } from "../framework";

const point = coordinatesSearchableModel.extend({
  id: z.string(),
});

export const searchDataModel = z.object({
  origin: z.object(point.shape, { required_error: "Origin is mandatory" }),
  destination: z.object(point.shape, { required_error: "Destination is mandatory" }),
  outbound: z.date({ coerce: true, required_error: "Departure date is mandatory" }),
  passengers: passengerPickerData,
  timeZoneOffset: z.number(),
});
export type SearchDataModel = z.infer<typeof searchDataModel>;

export const bookingSessionModel = z
  .object({
    sessionToken: z.string(),
    searchData: searchDataModel,
    offerSearch: z.object({
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

type Service = {
  search(data: SearchDataModel): Promise<void>;
  getOffers(): Promise<{ data: Offer[]; status: ResourceStatus }>;
  selectOffer(selectedOffer: NonNullable<BookingSessionModel["selected"]>): Promise<void>;
  getPriceQuote(): Promise<TripOfferPriceQuote>;
  getPaymentIntent(): Promise<Payment>;
  createOrder(
    data: OrderCreate,
  ): Promise<
    { success: true; order: Order } | { success: false; errors: z.ZodFormattedError<unknown> }
  >;
  confirmPayment(): Promise<void>;
  createOrderMarkups(
    data: MarkupsCreate,
  ): Promise<
    | { success: true; order: MarkupsCreate }
    | { success: false; errors: z.ZodFormattedError<unknown> }
  >;
};

const factory = clientServiceFactory<Service, RouteId>("/integration/trip-management");

export const methods = factory({
  confirmPayment: () => [],
  createOrder: (data: OrderCreate) => [data],
  createOrderMarkups: (data: MarkupsCreate) => [data],
  getOffers: () => [],
  getPaymentIntent: () => [],
  getPriceQuote: () => [],
  search: (data: SearchDataModel) => [data],
  selectOffer: (selectedOffer: NonNullable<BookingSessionModel["selected"]>) => [selectedOffer],
});

async function* yieldOffersAux(
  signal: { cancelled: boolean },
  ids: string[] = [],
): AsyncGenerator<Offer> {
  const result = await methods.getOffers();
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

type SearchMethod = (typeof methods)["search"];
type SelectOfferMethod = (typeof methods)["selectOffer"];

export default {
  ...methods,
  search: (data: Partial<SearchDataModel>): ReturnType<SearchMethod> =>
    methods.search(searchDataModel.parse(data)),
  yieldOffers,
  selectOffer: (...params: Parameters<SelectOfferMethod>): ReturnType<SelectOfferMethod> => {
    if (!params[0].optionIds.length) {
      throw new Error("No option selected");
    }

    return methods.selectOffer(...params);
  },
};
