import integrationInstances from "integration-instances";
import { methods } from "./trip-management";
import { getRandomAlphaNumericString } from "utils/random";
import utils from "./utils.server";
import { z } from "zod";
import { serverServiceFactory } from "../framework";
import { getOffers } from "./trip-management.server";

const factory = serverServiceFactory(methods);

export const POST = factory({
  confirmPayment(event) {
    const bookingSession = utils.getBookingSession(event);

    if (!bookingSession.paymentIntent) {
      throw new Error("Bad request");
    }

    utils.setBookingSession(
      { ...bookingSession, paymentIntent: { ...bookingSession.paymentIntent, confirmed: true } },
      event,
    );
  },
  async createOrder(event, data) {
    const bookingSession = utils.getBookingSession(event);

    try {
      const order = await integrationInstances.junctionMobileApi.orders.create({
        session: event.locals.session,
        data,
      });

      utils.setBookingSession({ ...bookingSession, order: { id: order.id } }, event);

      return { success: true, order };
    } catch (err) {
      if (err instanceof z.ZodError) {
        return { success: false, errors: err.format() };
      }

      throw err;
    }
  },
  async createOrderMarkups(event, data) {
    const bookingSession = utils.getBookingSession(event);

    try {
      const orderMarkups = await integrationInstances.junctionMobileApi.orders.createMarkups({
        session: event.locals.session,
        data,
      });

      utils.setBookingSession({ ...bookingSession, orderMarkups: { id: orderMarkups.id } }, event);

      return { success: true, order: orderMarkups };
    } catch (err) {
      if (err instanceof z.ZodError) {
        return { success: false, errors: err.format() };
      }

      throw err;
    }
  },
  getOffers,
  async getPaymentIntent(event) {
    const { session } = event.locals;
    const bookingSession = utils.getBookingSession(event);

    if (!bookingSession.priceQuote) {
      throw new Error("Bad request");
    }

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

    return paymentIntent;
  },
  async getPriceQuote(event) {
    const bookingSession = utils.getBookingSession(event);

    if (!bookingSession.priceQuote) {
      throw new Error("Bad request");
    }

    const priceQuote = await integrationInstances.junctionMobileApi.offers.get({
      session: event.locals.session,
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

    return priceQuote;
  },
  search(event, data) {
    utils.setBookingSession(
      { searchData: data, sessionToken: getRandomAlphaNumericString(32) },
      event,
    );
  },
  async selectOffer(event, selected) {
    const bookingSession = utils.getBookingSession(event);

    if (utils.offersEqual(selected, bookingSession.selected)) {
      return;
    }

    if (!(selected && bookingSession.sessionToken)) {
      throw new Error("Bad request");
    }

    const priceQuote = await integrationInstances.junctionMobileApi.offers.create({
      session: event.locals.session,
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
  },
});
