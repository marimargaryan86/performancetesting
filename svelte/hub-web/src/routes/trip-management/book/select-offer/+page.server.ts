import integrationInstances from "integration-instances";
import type { ResourceStatus } from "integration/junction-mobile-api/schemas/common";
import type { OfferModel } from "integration/junction-mobile-api/schemas/offer";
import type { TripCandidatesSearchModel } from "integration/junction-mobile-api/schemas/trip";
import type { PlaceModel } from "integration/junction-mobile-api/schemas/place";
import bookingManager, { type SearchDataModel } from "../booking-manager.server";
import { getActionRequestJsonData } from "utils/common";
import { z } from "zod";
import { priceModel } from "integration/junction-mobile-api/schemas/price";
import { getSession } from "utils/auth";

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
  const session = getSession(event);
  const searchData = bookingManager.getSearchData(event);

  try {
    const [origin, destination, result] = await Promise.all([
      integrationInstances.junctionMobileApi.places.getPlace({ session, id: searchData.origin.id }),
      integrationInstances.junctionMobileApi.places.getPlace({
        session,
        id: searchData.destination.id,
      }),
      bookingManager.getOffers({ session, data: searchData, event }),
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

const selectActionData = z.object({
  offerId: z.string().uuid(),
  optionIds: z.array(z.string().uuid()),
  originalPrice: priceModel.model,
});
export type SelectActionData = z.infer<typeof selectActionData>;

export const actions = {
  async poll(event): Promise<{ status: ResourceStatus; offers: OfferModel[] }> {
    try {
      const searchData = bookingManager.getSearchData(event);
      const result = await bookingManager.getOffers({
        session: getSession(event),
        data: searchData,
        event,
      });

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

    try {
      const data = await getActionRequestJsonData(event, selectActionData);

      // Offer and options have been selected before, don't update session.
      if (
        searchData.offerId === data.offerId &&
        searchData.optionIds?.join(",") === data.optionIds.join(",")
      ) {
        return;
      }

      bookingManager.setSearchData(
        {
          ...searchData,
          offerId: data.offerId,
          optionIds: data.optionIds,
          paymentIntent: undefined,
          originalPrice: data.originalPrice,
          priceQuoteId: undefined,
        },
        event,
      );
    } catch {
      return;
    }
  },
};
