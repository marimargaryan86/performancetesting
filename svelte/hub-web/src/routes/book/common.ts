import type { RequestEvent } from "@sveltejs/kit";
import type { PlaceModel } from "models/booking/location";
import jwt from "jsonwebtoken";
import { getRandomAlphaNumericString } from "utils/random";
import type { TripCandidatesModel } from "models/booking/trip";
import type { PaymentIntentModel } from "models/booking/payment";

export const SEARCH_TOKEN = "search-token";
export const JWT_SIGNATURE = "search-token";

export type PassengerCountData = {
  adults: number;
  children: number;
  infants: number;
};

export type SearchData = {
  sessionToken: string;
  originId: string;
  destinationId: string;
  departureAfter: Date;
  passengers: PassengerCountData;
  tripCandidatesSearchId?: string;
  offerId?: string;
  optionIds?: string[];
  priceQuoteId?: string;
  paymentIntent?: PaymentIntentModel;
  orderId?: string;
};

export type ResolvedSearchData = {
  sessionToken: string;
  origin: PlaceModel;
  destination: PlaceModel;
  departureAfter: Date;
  passengers: PassengerCountData;
  tripCandidatesSearch?: TripCandidatesModel;
  paymentIntent?: PaymentIntentModel;
};

function getTokenSearchData(event: RequestEvent): SearchData | undefined {
  const searchToken = event.cookies.get(SEARCH_TOKEN);

  if (!searchToken) {
    return undefined;
  }

  const searchData = jwt.decode(searchToken) as Omit<SearchData, "departureAfter"> & {
    departureAfter: string;
  };

  return { ...searchData, departureAfter: new Date(searchData.departureAfter) };
}

// eslint-disable-next-line complexity
function getQuerySearchData(event: RequestEvent): SearchData | undefined {
  const originId = event.url.searchParams.get("origin")?.toString();
  const destinationId = event.url.searchParams.get("destination")?.toString();
  const departureAfter = new Date(event.url.searchParams.get("outbound")?.toString() ?? "");
  const adults = Number(event.url.searchParams.get("adults")?.toString() ?? 0);
  const children = Number(event.url.searchParams.get("children")?.toString() ?? 0);
  const infants = Number(event.url.searchParams.get("infants")?.toString() ?? 0);

  if (
    !originId ||
    !destinationId ||
    isNaN(departureAfter.getTime()) ||
    isNaN(adults) ||
    isNaN(children) ||
    isNaN(infants)
  ) {
    return undefined;
  }

  return {
    sessionToken: getRandomAlphaNumericString(32),
    originId,
    destinationId,
    departureAfter,
    passengers: {
      adults,
      children,
      infants,
    },
  };
}

function searchDataEqual(searchData1: SearchData, searchData2: SearchData): boolean {
  return (
    searchData1.originId === searchData2.originId &&
    searchData1.destinationId === searchData2.destinationId &&
    searchData1.departureAfter.toLocaleDateString("sv-SE") ===
      searchData2.departureAfter.toLocaleDateString("sv-SE") &&
    searchData1.passengers.adults === searchData2.passengers.adults &&
    searchData1.passengers.children === searchData2.passengers.children &&
    searchData1.passengers.infants === searchData2.passengers.infants
  );
}

export function getSearchData(
  event: RequestEvent,
  location: "token" | "query" = "token",
): SearchData | undefined {
  const tokenSearchData = getTokenSearchData(event);

  if (location === "token") {
    return tokenSearchData;
  }

  const querySearchData = getQuerySearchData(event);

  if (!querySearchData) {
    return undefined;
  }

  if (!tokenSearchData) {
    return querySearchData;
  }

  return searchDataEqual(tokenSearchData, querySearchData) ? tokenSearchData : querySearchData;
}

export function setSearchData(data: SearchData, event: RequestEvent): void {
  event.cookies.set(SEARCH_TOKEN, jwt.sign(data, JWT_SIGNATURE), {
    path: "/",
    sameSite: "strict",
    httpOnly: true,
  });
}

export function parsePassengers(passengers: PassengerCountData): TripCandidatesModel["passengers"] {
  const adult = new Date();
  adult.setFullYear(adult.getFullYear() - 25);
  const child = new Date();
  child.setFullYear(child.getFullYear() - 7);
  const infant = new Date();
  infant.setFullYear(infant.getFullYear() - 1);

  return [
    ...Array<TripCandidatesModel["passengers"][number]>(passengers.adults).fill({
      dateOfBirth: adult,
    }),
    ...Array<TripCandidatesModel["passengers"][number]>(passengers.children).fill({
      dateOfBirth: child,
    }),
    ...Array<TripCandidatesModel["passengers"][number]>(passengers.infants).fill({
      dateOfBirth: infant,
    }),
  ];
}
