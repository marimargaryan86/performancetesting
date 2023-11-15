import integrationInstances from "integration-instances";
import type { Offer } from "integration/junction-mobile-api/schemas/offer";
import type { Place } from "integration/junction-mobile-api/schemas/place";
import tripManagement, {
  type BookingSessionModel,
  type SearchDataModel,
} from "../../../integration/trip-management/trip-management";
import utils from "../../../integration/trip-management/utils.server";
import { redirect } from "@sveltejs/kit";
import routeConfig from "routeConfig";
import type { ResourceStatus } from "integration/common/schemas/resource";

export async function load(event): Promise<{
  searchData: SearchDataModel;
  origin: Place;
  destination: Place;
  offers: { data: Offer[]; status: ResourceStatus };
  selectedOffer: BookingSessionModel["selected"];
  tripCandidates: BookingSessionModel["tripCandidates"];
}> {
  const session = event.locals.session;

  try {
    let bookingSession = utils.getBookingSession(event);

    if (!bookingSession.searchData) {
      throw new Error();
    }

    const { searchData } = bookingSession;

    const [offers, origin, destination] = await Promise.all([
      tripManagement.getOffers(event),
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
      tripCandidates: bookingSession.tripCandidates,
    };
  } catch {
    throw redirect(303, routeConfig.routes.tripManagement.routes.book.root);
  }
}
