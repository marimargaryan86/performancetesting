import { error, type RequestEvent } from "@sveltejs/kit";
import { SEARCH_TOKEN, type PassengerCountModel, type SearchData } from "../common";
import jwt from "jsonwebtoken";
import type { OfferPriceQuoteModel } from "models/booking/offer";
import integrationInstancesServer from "integration-instances-server";
import type { PlaceModel } from "models/booking/location";

function getSearchData(event: RequestEvent): SearchData {
  const token = event.cookies.get(SEARCH_TOKEN);

  if (!token) {
    throw error(400, { message: "Booking session not found" });
  }

  return jwt.decode(token) as SearchData;
}

export async function load(event): Promise<{
  searchData: {
    origin: PlaceModel;
    destination: PlaceModel;
    departureAfter: Date;
    passengers: PassengerCountModel;
  };
  priceQuote: OfferPriceQuoteModel;
}> {
  const searchData = getSearchData(event);

  if (!searchData.quoteId) {
    throw error(400, { message: "No quote ID found" });
  }

  try {
    const [origin, destination, priceQuote] = await Promise.all([
      integrationInstancesServer.junctionMobileApi.places.getPlace(searchData.originId),
      integrationInstancesServer.junctionMobileApi.places.getPlace(searchData.destinationId),
      integrationInstancesServer.junctionMobileApi.offers.getPriceQuote(searchData.quoteId),
    ]);

    return {
      searchData: {
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
  async poll(event): Promise<{ priceQuote: OfferPriceQuoteModel }> {
    const searchData = getSearchData(event);

    if (!searchData.quoteId) {
      throw error(400, { message: "No quote ID found" });
    }

    try {
      return {
        priceQuote: await integrationInstancesServer.junctionMobileApi.offers.getPriceQuote(
          searchData.quoteId,
        ),
      };
    } catch {
      throw error(404, { message: "Quote not found " });
    }
  },
};
