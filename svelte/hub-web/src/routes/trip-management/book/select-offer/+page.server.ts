import integrationInstances from "integration-instances";
import type { ResourceStatus } from "integration/junction-mobile-api/schemas/common";
import type { OfferModel } from "integration/junction-mobile-api/schemas/offer";
import type { PlaceModel } from "integration/junction-mobile-api/schemas/place";
import { getSession } from "utils/auth";
import tripManagement, {
  type BookingSessionModel,
  type SearchDataModel,
} from "../../../integration/trip-management/trip-management";
import utils from "../../../integration/trip-management/utils.server";
import { redirect } from "@sveltejs/kit";
import routeConfig from "routeConfig";

export async function load(event): Promise<{
  searchData: SearchDataModel;
  origin: PlaceModel;
  destination: PlaceModel;
  offers: { data: OfferModel[]; status: ResourceStatus };
  selectedOffer: BookingSessionModel["selected"];
  tripCandidates: BookingSessionModel["tripCandidates"];
}> {
  const session = getSession(event);

  try {
    let bookingSession = utils.getBookingSession(event);

    if (!bookingSession.searchData) {
      throw new Error();
    }

    const { searchData } = bookingSession;

    const [offers, origin, destination] = await Promise.all([
      tripManagement.getOffers(event),
      integrationInstances.junctionMobileApi.places.getPlace({ session, id: searchData.origin.id }),
      integrationInstances.junctionMobileApi.places.getPlace({
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
