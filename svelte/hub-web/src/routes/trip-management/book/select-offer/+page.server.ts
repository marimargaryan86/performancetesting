import { redirect } from "@sveltejs/kit";
import { getSearchData, parsePassengers, setSearchData, type ResolvedSearchData } from "../common";
import integrationInstances from "integration-instances";
import type { resourceStatus } from "integration/junction-mobile-api/schemas/common";
import type { z } from "zod";
import type { offerModel } from "integration/junction-mobile-api/schemas/offer";
import type { Infer } from "integration/junction-mobile-api/schema-model.server";
import routeConfig from "routeConfig";

export async function load(event): Promise<{
  searchData: ResolvedSearchData;
  selectedOffer?: { offerId: string; optionIds: string[] };
}> {
  const searchData = getSearchData(event, "query");

  if (!searchData) {
    setSearchData(undefined, event);

    throw redirect(303, routeConfig.tripManagement.book.root);
  }

  const [origin, destination] = await Promise.all([
    integrationInstances.junctionMobileApi.places.getPlace(searchData.originId),
    integrationInstances.junctionMobileApi.places.getPlace(searchData.destinationId),
  ]);

  // prettier-ignore
  const tripCandidatesSearch = await (searchData.tripCandidatesSearchId
    ? integrationInstances.junctionMobileApi.trips.getTripCandidatesSearch(
      searchData.tripCandidatesSearchId,
    )
    : integrationInstances.junctionMobileApi.trips.createTripCandidatesSearch({
      sessionToken: searchData.sessionToken,
      criteria: [
        {
          departureAfter: searchData.departureAfter,
          origin: origin.coordinates,
          destination: destination.coordinates,
        },
      ],
      passengers: parsePassengers(searchData.passengers),
      allowedLegTypeIds: ["rail"],
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
    | { status: Exclude<z.infer<typeof resourceStatus>, "completed"> }
    | { status: "completed"; offers: Infer<typeof offerModel>[] }
  > {
    const searchdata = getSearchData(event);
    const tripCandidatesSearchId = searchdata?.tripCandidatesSearchId;

    if (!tripCandidatesSearchId) {
      return { status: "failed" };
    }

    const tripCandidatesSearch =
      await integrationInstances.junctionMobileApi.trips.getTripCandidatesSearch(
        tripCandidatesSearchId,
      );

    if (tripCandidatesSearch.status === "completed") {
      return {
        status: "completed",
        offers: await integrationInstances.junctionMobileApi.trips.getTripCandidatesOffers(
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

    const priceQuote = await integrationInstances.junctionMobileApi.offers.createPriceQuote({
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
