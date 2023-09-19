import integrationInstances from "integration-instances";
import type { ResourceStatus } from "integration/junction-mobile-api/schemas/common";
import type { OfferModel } from "integration/junction-mobile-api/schemas/offer";
import type { TripCandidatesSearchModel } from "integration/junction-mobile-api/schemas/trip";
import type { PlaceModel } from "integration/junction-mobile-api/schemas/place";
import bookingManager, { type SearchDataModel } from "../booking-manager.server";

type LoadReturnType = {
  searchData: {
    passengers: SearchDataModel["passengers"];
    origin: PlaceModel;
    destination: PlaceModel;
    outbound: Date;
    offerId?: string;
    optionIds?: string[];
  };
  tripCandidates: {
    id: string;
    expiresAt: Date;
    offers: OfferModel[];
    status: TripCandidatesSearchModel["status"];
  };
};

export async function load(event): Promise<LoadReturnType> {
  const searchData = bookingManager.getSearchData(event);

  try {
    const [origin, destination, result] = await Promise.all([
      integrationInstances.junctionMobileApi.places.getPlace(searchData.origin.id),
      integrationInstances.junctionMobileApi.places.getPlace(searchData.destination.id),
      bookingManager.getOffers(searchData, event),
    ]);

    bookingManager.setSearchData(
      {
        ...searchData,
        sessionToken: result.sessionToken,
        tripCandidatesId: result.tripCandidatesId,
      },
      event,
    );

    return {
      searchData: {
        passengers: searchData.passengers,
        origin,
        destination,
        outbound: searchData.outbound,
        offerId: searchData.offerId,
        optionIds: searchData.optionIds,
      },
      tripCandidates: {
        id: result.tripCandidatesId,
        expiresAt: result.expiresAt,
        offers: result.offers,
        status: result.status,
      },
    };
  } catch (err) {
    throw bookingManager.rootRedirect(event);
  }
}

export const actions = {
  async poll(event): Promise<{ status: ResourceStatus; offers: OfferModel[] }> {
    try {
      const searchData = bookingManager.getSearchData(event);
      const result = await bookingManager.getOffers(searchData, event);

      return {
        status: result.status,
        offers: result.offers,
      };
    } catch {
      return { status: "failed", offers: [] };
    }
  },
  async select(event): Promise<void> {
    const searchData = bookingManager.getSearchData(event);
    const formData = await event.request.formData();
    const offerId = formData.get("offerId")?.toString();
    const optionIds = formData.get("optionIds")?.toString().split(",");

    if (!(offerId && optionIds?.length)) {
      return;
    }

    // Offer and options have been selected before, don't update session.
    if (searchData.offerId === offerId && searchData.optionIds?.join(",") === optionIds.join(",")) {
      return;
    }

    bookingManager.setSearchData(
      {
        ...searchData,
        offerId,
        optionIds,
        paymentIntent: undefined,
      },
      event,
    );
  },
};
