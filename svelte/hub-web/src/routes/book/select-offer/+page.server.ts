import { error } from "@sveltejs/kit";
import { getSearchData, parsePassengers, setSearchData, type ResolvedSearchData } from "../common";
import integrationInstancesServer from "integration-instances-server";
import type { TripCandidatesSearchStatus } from "integration/junction-mobile-api/schemas/trip";
import type { OfferModel } from "models/booking/offer";

export async function load(event): Promise<{
  searchData: ResolvedSearchData;
  selectedOffer?: { offerId: string; optionIds: string[] };
}> {
  const searchData = getSearchData(event, "query");

  if (!searchData) {
    throw error(400, "Invalid search data");
  }

  const [origin, destination] = await Promise.all([
    integrationInstancesServer.junctionMobileApi.places.getPlace(searchData.originId),
    integrationInstancesServer.junctionMobileApi.places.getPlace(searchData.destinationId),
  ]);

  // prettier-ignore
  const tripCandidatesSearch = await (searchData.tripCandidatesSearchId
    ? integrationInstancesServer.junctionMobileApi.trips.getTripCandidatesSearch(
      searchData.tripCandidatesSearchId,
    )
    : integrationInstancesServer.junctionMobileApi.trips.createTripCandidatesSearch({
      sessionToken: searchData.sessionToken,
      criteria: [
        {
          departureAfter: searchData.departureAfter,
          origin: origin.coordinates,
          destination: destination.coordinates,
        },
      ],
      passengers: parsePassengers(searchData.passengers),
    }));

  setSearchData({ ...searchData, tripCandidatesSearchId: tripCandidatesSearch.id }, event);

  return {
    searchData: {
      sessionToken: searchData.sessionToken,
      origin,
      destination,
      departureAfter: searchData.departureAfter,
      passengers: searchData.passengers,
      tripCandidatesSearch,
    },
    selectedOffer:
      searchData.offerId && searchData.optionIds
        ? { offerId: searchData.offerId, optionIds: searchData.optionIds }
        : undefined,
  };
}

export const actions = {
  async poll(
    event,
  ): Promise<
    | { status: Exclude<TripCandidatesSearchStatus, "completed"> }
    | { status: "completed"; offers: OfferModel[] }
  > {
    const searchdata = getSearchData(event);
    const tripCandidatesSearchId = searchdata?.tripCandidatesSearchId;

    if (!tripCandidatesSearchId) {
      return { status: "failed" };
    }

    const tripCandidatesSearch =
      await integrationInstancesServer.junctionMobileApi.trips.getTripCandidatesSearch(
        tripCandidatesSearchId,
      );

    if (tripCandidatesSearch.status === "completed") {
      return {
        status: "completed",
        offers: await integrationInstancesServer.junctionMobileApi.trips.getTripCandidatesOffers(
          tripCandidatesSearchId,
        ),
      };
    }

    return { status: tripCandidatesSearch.status };
  },
  async select(event): Promise<void> {
    const formData = await event.request.formData();
    const searchData = getSearchData(event);
    const offerId = formData.get("offerId")?.toString();
    const optionIds = formData.get("optionIds")?.toString().split(",");

    if (!searchData || !offerId || !optionIds) {
      return;
    }

    if (searchData.offerId === offerId && searchData.optionIds?.join(",") === optionIds.join(",")) {
      return;
    }

    const priceQuote = await integrationInstancesServer.junctionMobileApi.offers.createPriceQuote({
      sessionToken: searchData.sessionToken,
      offerId,
      optionIds,
    });

    setSearchData(
      { ...searchData, offerId, optionIds, priceQuoteId: priceQuote.id, paymentIntent: undefined },
      event,
    );
  },
};
