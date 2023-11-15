import * as devalue from "devalue";
import { getSession } from "utils/auth";
import type { RequestEvent } from "./$types";
import type { SessionModel } from "models/user";
import integrationInstances from "integration-instances";
import type { BookingSessionModel } from "./trip-management";
import { getRandomAlphaNumericString } from "utils/random";
import type { TripCandidateSearchCreate } from "integration/junction-mobile-api/schemas/trip-candidate";
import { getMinDate } from "utils/date-time";
import utils from "./utils.server";
import type { MaybePromise } from "@sveltejs/kit";
import type { OrderCreate } from "integration/junction-mobile-api/schemas/order";
import { z } from "zod";
import type { MarkupsCreate } from "integration/junction-mobile-api/schemas/markups";

function parsePassengers(
  passengers: NonNullable<BookingSessionModel["searchData"]>["passengers"],
): TripCandidateSearchCreate["passengers"] {
  const adult = new Date();
  adult.setFullYear(adult.getFullYear() - 30);
  const child = new Date();
  child.setFullYear(child.getFullYear() - 7);
  const infant = new Date();
  infant.setFullYear(infant.getFullYear() - 1);

  return [
    ...Array(passengers.adults).fill({ birthDate: adult }),
    ...Array(passengers.children).fill({ birthDate: child }),
    ...Array(passengers.infants).fill({ birthDate: infant }),
  ];
}

function offersEqual(
  offerA: BookingSessionModel["selected"],
  offerB: BookingSessionModel["selected"],
): boolean {
  return Boolean(
    offerA &&
      offerB &&
      offerA.offerId === offerB.offerId &&
      JSON.stringify(offerA.optionIds) === JSON.stringify(offerB.optionIds),
  );
}

async function search(event: RequestEvent): Promise<Response> {
  const searchData: BookingSessionModel["searchData"] = devalue.parse(await event.request.text());
  utils.setBookingSession({ searchData, sessionToken: getRandomAlphaNumericString(32) }, event);

  return new Response(undefined, { status: 204 });
}

async function getTripCandidates(
  session: SessionModel,
  {
    searchData,
    tripCandidates,
    sessionToken,
  }: Pick<BookingSessionModel, "searchData" | "tripCandidates" | "sessionToken">,
): Promise<NonNullable<BookingSessionModel["tripCandidates"]>> {
  if (!(searchData && sessionToken)) {
    throw new Error("Missing data");
  }

  if (tripCandidates && tripCandidates.expiresAt > new Date()) {
    try {
      const result = await integrationInstances.junctionMobileApi.simpleOfferSearches.get({
        id: tripCandidates.id,
        session,
      });

      return { id: result.id, expiresAt: result.expiresAt, status: result.status };
    } catch {
      //
    }
  }

  const result = await integrationInstances.junctionMobileApi.simpleOfferSearches.create({
    session,
    data: {
      sessionToken,
      passengers: parsePassengers(searchData.passengers),
      allowedSegmentTypes: ["rail"],
      criteria: { ...searchData, departureAfter: searchData.outbound },
    },
  });

  return { id: result.id, expiresAt: result.expiresAt, status: result.status };
}

async function getOffers(session: SessionModel, event: RequestEvent): Promise<Response> {
  const bookingSession = utils.getBookingSession(event);
  const sessionToken = bookingSession.sessionToken ?? getRandomAlphaNumericString(32);
  const tripCandidates = await getTripCandidates(session, {
    searchData: bookingSession.searchData,
    sessionToken,
    tripCandidates: bookingSession.tripCandidates,
  });
  const { data: offers } =
    await integrationInstances.junctionMobileApi.simpleOfferSearches.findOffers({
      session,
      simpleOfferSearchId: tripCandidates.id,
    });

  utils.setBookingSession(
    {
      ...bookingSession,
      offers: offers.length
        ? { expiresAt: getMinDate(...offers.map((item) => item.expiresAt)) }
        : undefined,
      tripCandidates,
      sessionToken,
    },
    event,
  );

  return new Response(devalue.stringify({ data: offers, status: tripCandidates.status }));
}

async function selectOffer(session: SessionModel, event: RequestEvent): Promise<Response> {
  const bookingSession = utils.getBookingSession(event);
  const selected: BookingSessionModel["selected"] = devalue.parse(await event.request.text());

  if (offersEqual(selected, bookingSession.selected)) {
    return new Response(undefined, { status: 204 });
  }

  if (!(selected && bookingSession.sessionToken)) {
    return new Response(undefined, { status: 400 });
  }

  const priceQuote = await integrationInstances.junctionMobileApi.offers.create({
    session,
    data: {
      sessionToken: bookingSession.sessionToken,
      offerId: selected.offerId,
      optionIds: selected.optionIds,
    },
  });

  utils.setBookingSession(
    {
      ...bookingSession,
      selected,
      priceQuote: {
        id: priceQuote.id,
        status: priceQuote.status,
        expiresAt: priceQuote.expiresAt,
      },
      // Unset payment intent when a new price quote is created
      paymentIntent: undefined,
    },
    event,
  );

  return new Response(undefined, { status: 204 });
}

async function getPriceQuote(session: SessionModel, event: RequestEvent): Promise<Response> {
  const bookingSession = utils.getBookingSession(event);

  if (!bookingSession.priceQuote) {
    return new Response(undefined, { status: 400 });
  }

  try {
    const priceQuote = await integrationInstances.junctionMobileApi.offers.get({
      session,
      id: bookingSession.priceQuote.id,
    });

    utils.setBookingSession(
      {
        ...bookingSession,
        priceQuote: {
          id: priceQuote.id,
          status: priceQuote.status,
          expiresAt: priceQuote.expiresAt,
        },
      },
      event,
    );

    return new Response(devalue.stringify(priceQuote));
  } catch {
    return new Response(undefined, { status: 400 });
  }
}

async function getPaymentIntent(session: SessionModel, event: RequestEvent): Promise<Response> {
  const bookingSession = utils.getBookingSession(event);

  if (!bookingSession.priceQuote) {
    return new Response(undefined, { status: 400 });
  }

  try {
    const priceQuote = await integrationInstances.junctionMobileApi.offers.get({
      session,
      id: bookingSession.priceQuote?.id,
    });

    if (!priceQuote.price.total) {
      throw new Error();
    }

    const paymentIntent = await integrationInstances.junctionMobileApi.payments.create({
      session,
      data: priceQuote.price.total,
    });

    utils.setBookingSession({ ...bookingSession, paymentIntent }, event);

    return new Response(devalue.stringify(paymentIntent));
  } catch {
    return new Response(undefined, { status: 400 });
  }
}

function confirmPayment(event: RequestEvent): Response {
  const bookingSession = utils.getBookingSession(event);

  if (!bookingSession.paymentIntent) {
    return new Response(undefined, { status: 400 });
  }

  utils.setBookingSession(
    { ...bookingSession, paymentIntent: { ...bookingSession.paymentIntent, confirmed: true } },
    event,
  );

  return new Response();
}

async function createOrder(session: SessionModel, event: RequestEvent): Promise<Response> {
  const bookingSession = utils.getBookingSession(event);
  const data: OrderCreate = devalue.parse(await event.request.text());

  try {
    const order = await integrationInstances.junctionMobileApi.orders.create({
      session,
      data,
    });

    utils.setBookingSession({ ...bookingSession, order: { id: order.id } }, event);

    return new Response(devalue.stringify(order), { status: 201 });
  } catch (err) {
    if (err instanceof z.ZodError) {
      return new Response(devalue.stringify(err.format()), { status: 422 });
    }
    return new Response(undefined, { status: 400 });
  }
}

async function createOrderMarkups(session: SessionModel, event: RequestEvent): Promise<Response> {
  const bookingSession = utils.getBookingSession(event);
  const data: MarkupsCreate = devalue.parse(await event.request.text());

  try {
    const orderMarkups = await integrationInstances.junctionMobileApi.orders.createMarkups({
      session,
      data,
    });

    utils.setBookingSession({ ...bookingSession, orderMarkups: { id: orderMarkups.id } }, event);

    return new Response(devalue.stringify(orderMarkups), { status: 201 });
  } catch (err) {
    if (err instanceof z.ZodError) {
      return new Response(devalue.stringify(err.format()), { status: 422 });
    }

    return new Response(undefined, { status: 400 });
  }
}

export function GET(event): Promise<Response> {
  const session = getSession(event);
  const action = event.url.searchParams.get("action")?.toString();

  switch (action) {
    case "get-offers":
      return getOffers(session, event);
    case "get-price-quote":
      return getPriceQuote(session, event);
    case "get-payment-intent":
      return getPaymentIntent(session, event);
    default:
      return new Promise((resolve) => resolve(new Response(undefined, { status: 400 })));
  }
}

export function POST(event): MaybePromise<Response> {
  const session = getSession(event);
  const action = event.url.searchParams.get("action")?.toString();

  switch (action) {
    case "search":
      return search(event);
    case "select-offer":
      return selectOffer(session, event);
    case "confirm-payment":
      return confirmPayment(event);
    case "create-order":
      return createOrder(session, event);
    case "create-order-markups":
      return createOrderMarkups(session, event);
    default:
      return new Promise((resolve) => resolve(new Response(undefined, { status: 400 })));
  }
}
