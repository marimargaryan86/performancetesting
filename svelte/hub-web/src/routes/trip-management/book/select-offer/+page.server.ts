import integrationInstances from "integration-instances";
import type { Offer } from "integration/junction-mobile-api/schemas/offer";
import type { Place } from "integration/junction-mobile-api/schemas/place";
import type {
  BookingSessionModel,
  SearchDataModel,
} from "../../../integration/trip-management/trip-management";
import utils from "../../../integration/trip-management/utils.server";
import { redirect } from "@sveltejs/kit";
import routeConfig from "routeConfig";
import type { ResourceStatus } from "integration/common/schemas/resource";
import { getOffers } from "../../../integration/trip-management/trip-management.server";

export async function load(event): Promise<{
  searchData: SearchDataModel;
  origin: Place;
  destination: Place;
  offers: { data: Offer[]; status: ResourceStatus };
  selectedOffer: BookingSessionModel["selected"];
  offerSearch: BookingSessionModel["offerSearch"];
}> {
  const session = event.locals.session;

  try {
    let bookingSession = utils.getBookingSession(event);

    if (!bookingSession.searchData) {
      throw new Error();
    }

    const { searchData } = bookingSession;

    const [offers, origin, destination] = await Promise.all([
      getOffers(event),
      integrationInstances.junctionMobileApi.places.get({ session, id: searchData.origin.id }),
      integrationInstances.junctionMobileApi.places.get({
        session,
        id: searchData.destination.id,
      }),
    ]);

    bookingSession = utils.getBookingSession(event);

    return {
      searchData,
      origin,
      destination,
      offers,
      selectedOffer: bookingSession.selected,
      offerSearch: bookingSession.offerSearch,
    };
  } catch {
    throw redirect(303, routeConfig.routes.tripManagement.routes.book.root);
  }
}
