import type { RequestEvent } from "@sveltejs/kit";
import jwt from "jsonwebtoken";
import { getRandomAlphaNumericString } from "utils/random";
import { URLExtended } from "utils/url";
import { tripSearchQueryData } from "./trip-search/trip-search.svelte";
import type { TripCandidatesSearchModel } from "integration/junction-mobile-api/schemas/trip";
import type { PaymentIntentModel } from "integration/junction-mobile-api/schemas/payment";
import type { PlaceModel } from "integration/junction-mobile-api/schemas/place";

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
  tripCandidatesSearch?: TripCandidatesSearchModel;
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

function getQuerySearchData(event: RequestEvent): SearchData | undefined {
  try {
    const url = new URLExtended(event.url, { querySchema: tripSearchQueryData });

    return {
      sessionToken: getRandomAlphaNumericString(32),
      originId: url.query.origin,
      destinationId: url.query.destination,
      departureAfter: url.query.outbound,
      passengers: {
        adults: url.query.adults,
        children: url.query.children,
        infants: url.query.infants,
      },
    };
  } catch (err) {
    return undefined;
  }
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

export function setSearchData(data: SearchData | undefined, event: RequestEvent): void {
  if (data === undefined) {
    event.cookies.delete(SEARCH_TOKEN, { path: "/", sameSite: "strict", httpOnly: true });

    return;
  }

  event.cookies.set(SEARCH_TOKEN, jwt.sign(data, JWT_SIGNATURE), {
    path: "/",
    sameSite: "strict",
    httpOnly: true,
  });
}

type Passenger = TripCandidatesSearchModel["passengers"][number];

export function parsePassengers(passengers: PassengerCountData): Passenger[] {
  const adult = new Date();
  adult.setFullYear(adult.getFullYear() - 25);
  const child = new Date();
  child.setFullYear(child.getFullYear() - 7);
  const infant = new Date();
  infant.setFullYear(infant.getFullYear() - 1);

  return [
    ...Array(passengers.adults)
      .fill(undefined)
      .map<Passenger>(() => ({ dateOfBirth: adult })),
    ...Array(passengers.children)
      .fill(undefined)
      .map<Passenger>(() => ({ dateOfBirth: child })),
    ...Array(passengers.infants)
      .fill(undefined)
      .map<Passenger>(() => ({ dateOfBirth: infant })),
  ];
}
