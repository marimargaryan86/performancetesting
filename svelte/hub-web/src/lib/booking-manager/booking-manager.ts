import { z } from "zod";
import * as MobileSchemas from "~/integration/junction-mobile-api/schemas";
import * as CommonSchemas from "~/integration/common/schemas";
import { Base64 } from "js-base64";
import * as devalue from "devalue";
import type { RequestEvent } from "@sveltejs/kit";
import { getRandomAlphaNumericString } from "$lib/utils/random";
import integrationInstancesClient from "~/integration-instances-client";
import { sleep } from "$lib/utils/common";

export const markupsModel: z.ZodType<Omit<MobileSchemas.MarkupsCreate, "orderId">> = z.object({
  serviceFee: CommonSchemas.priceModel.refine((value) => value.amount >= 0, {
    message: "Amount must be greater than or equal to 0",
    path: ["amount"],
  }),
  agencyMarkup: CommonSchemas.priceModel.refine((value) => value.amount >= 0, {
    message: "Amount must be greater than or equal to 0",
    path: ["amount"],
  }),
  totalToCollect: CommonSchemas.priceModel.refine((value) => value.amount >= 0, {
    message: "Amount must be greater than or equal 0",
    path: ["amount"],
  }),
});
export type Markups = z.infer<typeof markupsModel>;
export type PartialMarkups = Partial<Markups>;

const offerSearchModel = z.object({
  id: z.string().uuid(),
  status: CommonSchemas.resourceStatus,
  expiresAt: z.date(),
});

const selectedOfferModel = z.object({
  offerId: z.string().uuid(),
  optionIds: z.array(z.string()),
  originalPrice: CommonSchemas.priceModel,
});
type SelectedOffer = z.infer<typeof selectedOfferModel>;
export type PartialSelectedOffer = Partial<SelectedOffer>;

const priceQuoteModel = z.object({
  id: z.string().uuid(),
  status: CommonSchemas.resourceStatus,
  expiresAt: z.date(),
});

const orderModel = z.object({
  id: z.string().uuid(),
});
type Order = z.infer<typeof orderModel>;

const paymentIntentModel = MobileSchemas.paymentModel.extend({
  confirmed: z.boolean(),
});
export type PaymentIntent = z.infer<typeof paymentIntentModel>;

const searchDataModel = z.object({
  origin: MobileSchemas.placeModel,
  destination: MobileSchemas.placeModel,
  outbound: z.date(),
  inbound: z.date().optional(),
  passengers: z.array(z.date()),
  windowH: z.number().optional(),
  transportTypes: z.array(z.enum(CommonSchemas.transportTypes)),
});
export type SearchData = z.infer<typeof searchDataModel>;

// Validator for the search step of the flow
const bookingSessionSearchModel = z.object({
  sessionToken: z.string(),
  searchData: searchDataModel,
  offerSearch: offerSearchModel.refine((value) => value.expiresAt > new Date(), {
    message: "The offer has expired",
    path: ["offerSearch", "expiresAt"],
  }),
  selectedOffer: selectedOfferModel.optional(),
  priceQuote: priceQuoteModel.optional(),
});
export type BookingSessionSearch = z.infer<typeof bookingSessionSearchModel>;

// Validator for the selection step of the flow
const bookingSessionSelectModel = bookingSessionSearchModel.extend({
  offerSearch: offerSearchModel,
  selectedOffer: selectedOfferModel,
  priceQuote: priceQuoteModel.refine((value) => value.expiresAt > new Date(), {
    message: "The price quote has expired",
    path: ["priceQuote", "expiresAt"],
  }),
  payment: paymentIntentModel.optional(),
  order: orderModel.optional(),
  markups: markupsModel.optional(),
});
export type BookingSessionSelect = z.infer<typeof bookingSessionSelectModel>;

// Validator for the payment step of the flow
const bookingSessionPaymentModel = bookingSessionSelectModel.extend({
  priceQuote: priceQuoteModel,
  payment: paymentIntentModel,
  order: orderModel,
});
export type BookingSessionPayment = z.infer<typeof bookingSessionPaymentModel>;

/**
 * Decode a booking session cookie
 * @param cookie Cookie value
 * @param model Zod schema the value must validate against
 * @returns Validated model
 */
function decodeSessionCookie<TData>(cookie: string, model: z.ZodType<TData>): TData {
  return model.parse(devalue.parse(Base64.decode(cookie)));
}

/**
 * Encode a booking session cookie
 * @param data Data to encode
 * @returns Cookie value
 */
function encodeSessionCookie<TData>(model: z.ZodType<TData>, data: TData): string {
  return Base64.encode(devalue.stringify(model.parse(data)));
}

type Step = "search" | "select" | "payment";
type StepDataType<TStep extends Step> = TStep extends "search"
  ? BookingSessionSearch
  : TStep extends "select"
    ? BookingSessionSelect
    : TStep extends "payment"
      ? BookingSessionPayment
      : never;
type StepModelType<TStep extends Step> = TStep extends "search"
  ? BookingSessionSearch
  : TStep extends "select"
    ? BookingSessionSelect
    : TStep extends "payment"
      ? BookingSessionPayment
      : never;

function getModel(step: Step): z.ZodType {
  if (step === "search") {
    return bookingSessionSearchModel;
  } else if (step === "payment") {
    return bookingSessionPaymentModel;
  } else if (step === "select") {
    return bookingSessionSelectModel;
  }

  throw new Error("Unknown step");
}

export function getCookie<TStep extends Step>(
  step: TStep,
  event: RequestEvent,
): StepModelType<TStep> {
  return decodeSessionCookie(event.cookies.get("booking-session") ?? "[{}]", getModel(step));
}

export function setCookie<TStep extends Step>(step: TStep, data: StepDataType<TStep>): void {
  document.cookie = `booking-session=${encodeSessionCookie(getModel(step), data)}; path=/;`;
}

async function search(
  data: SearchData,
  useWindow: boolean,
): Promise<MobileSchemas.SimpleOfferSearch> {
  const sessionToken = getRandomAlphaNumericString(32);
  const offerSearch = await integrationInstancesClient.mobile.simpleOfferService.create({
    data: {
      criteria: {
        outbound: data.outbound,
        destination: data.destination.coordinates,
        origin: data.origin.coordinates,
        windowH: useWindow ? data.windowH : undefined,
      },
      passengers: data.passengers.map((birthDate) => ({ birthDate })),
      allowedSegmentTypes: data.transportTypes,
      sessionToken,
    },
  });

  setCookie("search", { sessionToken, offerSearch, searchData: data });

  return offerSearch;
}

async function* getOffersAux(
  offerSearchId: string,
  signal: AbortSignal,
  offerIds: string[],
): AsyncGenerator<MobileSchemas.Offer> {
  const offerSearch = await integrationInstancesClient.mobile.simpleOfferService.get({
    id: offerSearchId,
  });
  const offers = await integrationInstancesClient.mobile.simpleOfferService.findOffers({
    id: offerSearchId,
  });

  for (const offer of offers.data.filter((item) => !offerIds.includes(item.id))) {
    offerIds.push(offer.id);

    yield offer;
  }

  if (offerSearch.status === "pending" || offerSearch.status === "processing") {
    await sleep(2000);

    if (!signal.aborted) {
      yield* getOffersAux(offerSearchId, signal, offerIds);
    }
  }
}

function getOffers(
  offerSearchId: string,
  signal: AbortSignal,
): AsyncGenerator<MobileSchemas.Offer> {
  return getOffersAux(offerSearchId, signal, []);
}

async function selectOffer(
  session: BookingSessionSearch,
  offer: MobileSchemas.Offer,
  options: MobileSchemas.OfferOption[],
): Promise<void> {
  const selectedOffer: SelectedOffer = {
    offerId: offer.id,
    optionIds: options.map(({ id }) => id),
    originalPrice: options.reduce<CommonSchemas.Price>(
      (prev, curr) => ({
        currency: curr.price.total.currency,
        amount: prev.amount + curr.price.total.amount,
      }),
      // Should technically never happen since options would have to be empty
      { currency: "EUR", amount: 0 },
    ),
  };

  if (
    session.priceQuote &&
    session.selectedOffer?.offerId === selectedOffer.offerId &&
    session.selectedOffer.optionIds.join(",") === selectedOffer.optionIds.join(",")
  ) {
    // Price quote is already set and the selection has not changed
    return;
  }

  const priceQuote = await integrationInstancesClient.mobile.offers.create({
    data: {
      sessionToken: session.sessionToken,
      offerId: selectedOffer.offerId,
      optionIds: selectedOffer.optionIds,
    },
  });

  setCookie("select", { ...session, priceQuote, selectedOffer, payment: undefined });
}

async function getPriceQuote(
  session: BookingSessionSelect,
  priceQuoteId: string,
  signal: AbortSignal,
): Promise<MobileSchemas.TripOfferPriceQuoteCompleted> {
  const priceQuote = await integrationInstancesClient.mobile.offers.get({ id: priceQuoteId });

  setCookie("select", { ...session, priceQuote });

  if (priceQuote.status === "pending" || priceQuote.status === "processing") {
    await sleep(2000);

    if (!signal.aborted) {
      return getPriceQuote(session, priceQuoteId, signal);
    }
  }

  if (priceQuote.status === "completed" && priceQuote.price.total) {
    return priceQuote as MobileSchemas.TripOfferPriceQuoteCompleted;
  }

  throw new Error("Price quote failed");
}

async function getPayment(
  session: BookingSessionSelect,
  priceQuote: MobileSchemas.TripOfferPriceQuoteCompleted,
): Promise<PaymentIntent> {
  const paymentIntent = await integrationInstancesClient.mobile.payments.create({
    data: priceQuote.price.total,
  });

  const payment: PaymentIntent = { ...paymentIntent, confirmed: false };

  setCookie("select", { ...session, payment });

  return payment;
}

async function createOrder(
  session: BookingSessionSelect,
  data: {
    contact: MobileSchemas.ContactDetails;
    passengers: MobileSchemas.OrderPassenger[];
    payment: PaymentIntent;
    priceQuote: MobileSchemas.TripOfferPriceQuoteCompleted;
  },
): Promise<MobileSchemas.Order> {
  const order = await integrationInstancesClient.mobile.orders.create({
    data: {
      contact: data.contact,
      passengers: data.passengers,
      paymentId: data.payment.id,
      priceQuoteId: data.priceQuote.id,
    },
  });

  setCookie("select", { ...session, order });

  return order;
}

async function createMarkups(
  session: BookingSessionSelect,
  order: Order,
  data: Markups,
): Promise<MobileSchemas.Markups> {
  const markups = await integrationInstancesClient.mobile.orders.createMarkups({
    data: { ...data, orderId: order.id },
  });

  setCookie("select", { ...session, markups });

  return markups;
}

function confirmPayment(session: BookingSessionSelect, payment: PaymentIntent): PaymentIntent {
  const nextPayment: PaymentIntent = { ...payment, confirmed: true };

  setCookie("select", { ...session, payment: nextPayment });

  return nextPayment;
}

export const manager = {
  search,
  getOffers,
  selectOffer,
  getPriceQuote,
  getPayment,
  createOrder,
  createMarkups,
  confirmPayment,
};
