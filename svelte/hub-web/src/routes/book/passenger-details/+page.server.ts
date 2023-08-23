import { ActionFailure, error, fail } from "@sveltejs/kit";
import type { OfferPriceQuoteModel } from "models/booking/offer";
import integrationInstancesServer from "integration-instances-server";
import { getSearchData, type ResolvedSearchData } from "../common";

export async function load(event): Promise<{
  searchData: ResolvedSearchData;
  priceQuote: OfferPriceQuoteModel;
}> {
  const searchData = getSearchData(event);

  if (!searchData?.priceQuoteId) {
    throw error(400, { message: "No quote ID found" });
  }

  try {
    const [origin, destination, priceQuote] = await Promise.all([
      integrationInstancesServer.junctionMobileApi.places.getPlace(searchData.originId),
      integrationInstancesServer.junctionMobileApi.places.getPlace(searchData.destinationId),
      integrationInstancesServer.junctionMobileApi.offers.getPriceQuote(searchData.priceQuoteId),
    ]);

    return {
      searchData: {
        sessionToken: searchData.sessionToken,
        origin,
        destination,
        departureAfter: new Date(searchData.departureAfter),
        passengers: searchData.passengers,
      },
      priceQuote,
    };
  } catch {
    throw error(404, { message: "Quote not found" });
  }
}

export const actions = {
  async poll(
    event,
  ): Promise<{ priceQuote: OfferPriceQuoteModel } | ActionFailure<{ error: string }>> {
    const searchData = getSearchData(event);

    if (!searchData?.priceQuoteId) {
      throw error(400, { message: "No quote ID found" });
    }

    try {
      return {
        priceQuote: await integrationInstancesServer.junctionMobileApi.offers.getPriceQuote(
          searchData.priceQuoteId,
        ),
      };
    } catch {
      return fail(404, { error: "Quote not found" });
    }
  },
};
