import { ActionFailure, error, fail } from "@sveltejs/kit";
import integrationInstances from "integration-instances";
import { getSearchData, setSearchData, type ResolvedSearchData, type SearchData } from "../common";
import type { Infer } from "integration/junction-mobile-api/schema-model.server";
import type { tripOfferPriceQuoteModel } from "integration/junction-mobile-api/schemas/offer";
import type { paymentIntentModel } from "integration/junction-mobile-api/schemas/payment";

export type ActionPollReturnType = {
  priceQuote: Infer<typeof tripOfferPriceQuoteModel>;
  paymentIntent?: Infer<typeof paymentIntentModel>;
};

async function getPriceQuoteAndPaymentIntent(searchData: SearchData): Promise<{
  priceQuote: Infer<typeof tripOfferPriceQuoteModel>;
  paymentIntent?: Infer<typeof paymentIntentModel>;
}> {
  if (!searchData.priceQuoteId) {
    throw error(400, { message: "No quote ID found" });
  }

  let priceQuote: Infer<typeof tripOfferPriceQuoteModel> | undefined;

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
  priceQuote: Infer<typeof tripOfferPriceQuoteModel>;
}> {
  const searchData = getSearchData(event);

  if (!searchData) {
    throw error(400, { message: "No search data found" });
  }

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
