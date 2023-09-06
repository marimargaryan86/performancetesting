import { ActionFailure, error, fail, redirect } from "@sveltejs/kit";
import type { TripOfferPriceQuoteModel } from "integration/junction-mobile-api/schemas/offer";
import type { PaymentIntentModel } from "integration/junction-mobile-api/schemas/payment";
import integrationInstances from "integration-instances";
import { getSearchData, setSearchData, type ResolvedSearchData, type SearchData } from "../common";
import routeConfig from "routeConfig";

export type ActionPollReturnType = {
  priceQuote: TripOfferPriceQuoteModel;
  paymentIntent?: PaymentIntentModel;
};

async function getPriceQuoteAndPaymentIntent(searchData: SearchData): Promise<{
  priceQuote: TripOfferPriceQuoteModel;
  paymentIntent?: PaymentIntentModel;
}> {
  if (!searchData.priceQuoteId) {
    throw error(400, { message: "No quote ID found" });
  }

  let priceQuote: TripOfferPriceQuoteModel | undefined;

  try {
    priceQuote = await integrationInstances.junctionMobileApi.offers.getPriceQuote(
      searchData.priceQuoteId,
    );
  } catch {
    priceQuote = undefined;
  }

  if (!priceQuote) {
    throw error(404, { message: "Quote not found" });
  }

  let paymentIntent = searchData.paymentIntent;

  if (!paymentIntent && priceQuote.price) {
    try {
      paymentIntent = await integrationInstances.junctionMobileApi.payments.createPayment(
        priceQuote.price,
      );
    } catch {
      throw error(500, { message: "Failed to create payment intent" });
    }
  }

  return { priceQuote, paymentIntent };
}

export async function load(event): Promise<{
  searchData: ResolvedSearchData;
  priceQuote: TripOfferPriceQuoteModel;
}> {
  const searchData = getSearchData(event);

  if (!searchData) {
    setSearchData(undefined, event);

    throw redirect(303, routeConfig.tripManagement.book.root);
  }

  try {
    const [origin, destination, { priceQuote, paymentIntent }] = await Promise.all([
      integrationInstances.junctionMobileApi.places.getPlace(searchData.originId),
      integrationInstances.junctionMobileApi.places.getPlace(searchData.destinationId),
      getPriceQuoteAndPaymentIntent(searchData),
    ]);

    setSearchData({ ...searchData, paymentIntent }, event);

    return {
      searchData: {
        sessionToken: searchData.sessionToken,
        origin,
        destination,
        departureAfter: new Date(searchData.departureAfter),
        passengers: searchData.passengers,
        paymentIntent,
      },
      priceQuote,
    };
  } catch {
    setSearchData(undefined, event);

    throw redirect(303, routeConfig.tripManagement.book.root);
  }
}

export const actions = {
  async poll(event): Promise<ActionPollReturnType | ActionFailure<{ error: string }>> {
    const searchData = getSearchData(event);

    if (!searchData) {
      throw error(400, { message: "No search data found" });
    }

    try {
      const { priceQuote, paymentIntent } = await getPriceQuoteAndPaymentIntent(searchData);

      setSearchData({ ...searchData, paymentIntent }, event);

      return { priceQuote, paymentIntent };
    } catch (err) {
      const castErr = err as { status: number; body: { message: string } };

      return fail(castErr.status, { error: castErr.body.message });
    }
  },
};
