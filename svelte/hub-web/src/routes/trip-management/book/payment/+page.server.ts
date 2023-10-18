import { redirect } from "@sveltejs/kit";
import integrationInstances from "integration-instances";
import type { TripOfferPriceQuoteModel } from "integration/junction-mobile-api/schemas/offer";
import { getSession } from "utils/auth";
import utils from "../../../integration/trip-management/utils.server";
import routeConfig from "routeConfig";
import type {
  BookingSessionModel,
  SearchDataModel,
} from "../../../integration/trip-management/trip-management";

export async function load(event): Promise<{
  searchData: SearchDataModel;
  priceQuote: TripOfferPriceQuoteModel;
  selected: NonNullable<BookingSessionModel["selected"]>;
  paymentIntent: BookingSessionModel["paymentIntent"];
}> {
  const session = getSession(event);

  try {
    const bookingSession = utils.getBookingSession(event);

    if (!(bookingSession.searchData && bookingSession.priceQuote && bookingSession.selected)) {
      throw redirect(303, routeConfig.routes.tripManagement.routes.book.root);
    }

    const priceQuote = await integrationInstances.junctionMobileApi.offers.getPriceQuote({
      session,
      id: bookingSession.priceQuote.id,
    });

    return {
      searchData: bookingSession.searchData,
      priceQuote,
      selected: bookingSession.selected,
      paymentIntent: bookingSession.paymentIntent,
    };
  } catch {
    throw redirect(303, routeConfig.routes.tripManagement.routes.book.root);
  }
}
