import integrationInstancesServer from "integration-instances-server";
import type { PlaceModel } from "models/booking/location";
import type { TripCandidatesModel } from "models/booking/trip";
import type { RequestEvent } from "./$types";
import type { TripCandidatesSearchStatus } from "integration/junction-mobile-api/schemas/trip";
import type { OfferModel } from "models/booking/offer";
import jwt from "jsonwebtoken";
import {
  SEARCH_TOKEN,
  type SearchData,
  getPassengers,
  parsePassengers,
  JWT_SIGNATURE,
  getOrigDest,
} from "../common";

function isNewSearch(nextSearch: SearchData, existingSearch?: SearchData): boolean {
  return (
    !existingSearch ||
    existingSearch.departureAfter !== nextSearch.departureAfter ||
    existingSearch.destinationId !== nextSearch.destinationId ||
    existingSearch.originId !== nextSearch.originId ||
    existingSearch.passengers.adults !== nextSearch.passengers.adults ||
    existingSearch.passengers.children !== nextSearch.passengers.children ||
    existingSearch.passengers.infants !== nextSearch.passengers.infants
  );
}

function getSearchData(event: RequestEvent): SearchData | undefined {
  const token = event.cookies.get(SEARCH_TOKEN);
  const existingSearch = token ? (jwt.decode(token) as SearchData) : undefined;
  const originId = event.url.searchParams.get("origin");
  const destinationId = event.url.searchParams.get("destination");
  const departureAfter = new Date(event.url.searchParams.get("outbound") ?? "");
  const passengers = getPassengers(event);

  if (!(originId && destinationId && !isNaN(departureAfter.getTime()))) {
    return undefined;
  }

  const nextSearch: SearchData = {
    originId,
    destinationId,
    departureAfter: departureAfter.toISOString(),
    passengers,
  };

  if (isNewSearch(nextSearch, existingSearch)) {
    return nextSearch;
  }

  return existingSearch;
}

type LoadReturnType = {
  origin?: PlaceModel;
  destination?: PlaceModel;
  tripCandidatesSearch?: TripCandidatesModel;
  selectedOffer?: { offerId: string; optionIds: string[] };
};

export async function load(event): Promise<LoadReturnType> {
  const searchData = getSearchData(event);

  if (!searchData) {
    return {};
  }

  const { origin, destination } = await getOrigDest(searchData.originId, searchData.destinationId);

  if (!(origin && destination)) {
    return {};
  }

  try {
    // prettier-ignore
    const tripCandidatesSearch = searchData.tripCandidatesSearchId
      ?
      await integrationInstancesServer.junctionMobileApi.trips.getTripCandidatesSearch(
        searchData.tripCandidatesSearchId,
      )
      : await integrationInstancesServer.junctionMobileApi.trips.createTripCandidatesSearch({
        passengers: parsePassengers(searchData.passengers),
        criteria: [
          {
            departureAfter: new Date(searchData.departureAfter),
            destination: destination.coordinates,
            origin: origin.coordinates,
          },
        ],
      });

    searchData.tripCandidatesSearchId = tripCandidatesSearch.id;
    event.cookies.set(SEARCH_TOKEN, jwt.sign(JSON.stringify(searchData), JWT_SIGNATURE), {
      path: "/",
      httpOnly: true,
      sameSite: "strict",
    });

    return {
      origin,
      destination,
      tripCandidatesSearch,
      selectedOffer:
        searchData.offerId && searchData.optionIds
          ? {
              offerId: searchData.offerId,
              optionIds: searchData.optionIds,
            }
          : undefined,
    };
  } catch (err) {
    event.cookies.delete(SEARCH_TOKEN, { path: "/", httpOnly: true, sameSite: "strict" });

    return { origin, destination };
  }
}

export const actions = {
  async poll(
    event,
  ): Promise<
    | { status: Exclude<TripCandidatesSearchStatus, "completed"> }
    | { status: "completed"; offers: OfferModel[] }
  > {
    const formData = await event.request.formData();
    const tripCandidatesSearchId = formData.get("tripCandidatesSearchId")?.toString();

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
    const token = event.cookies.get(SEARCH_TOKEN);
    const formData = await event.request.formData();
    const offerId = formData.get("offerId")?.toString();
    const optionIds = formData.get("optionIds")?.toString().split(",");

    if (!(token && offerId && optionIds)) {
      return;
    }

    const priceQuote = await integrationInstancesServer.junctionMobileApi.offers.createPriceQuote({
      offerId,
      optionIds,
    });

    const existingSearch = jwt.decode(token) as SearchData;
    existingSearch.offerId = offerId;
    existingSearch.optionIds = optionIds;
    existingSearch.quoteId = priceQuote.id;

    event.cookies.set(SEARCH_TOKEN, jwt.sign(existingSearch, JWT_SIGNATURE), {
      path: "/",
      httpOnly: true,
      sameSite: "strict",
    });
  },
};
