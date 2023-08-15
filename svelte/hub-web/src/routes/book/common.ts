import type { RequestEvent } from "@sveltejs/kit";
import integrationInstancesServer from "integration-instances-server";
import type { PlaceModel } from "models/booking/location";
import type { TripCandidatesModel } from "models/booking/trip";

export const SEARCH_TOKEN = "search-token";
export const JWT_SIGNATURE = "trip-candidates-search";

export type PassengerCountModel = {
  adults: number;
  children: number;
  infants: number;
};

export type SearchData = {
  originId: string;
  destinationId: string;
  departureAfter: string;
  passengers: PassengerCountModel;
  tripCandidatesSearchId?: string;
  offerId?: string;
  optionIds?: string[];
  quoteId?: string;
};

export async function getOrigDest(
  originId: string,
  destinationId: string,
): Promise<{ origin?: PlaceModel; destination?: PlaceModel }> {
  try {
    const [origin, destination] = await Promise.all([
      integrationInstancesServer.junctionMobileApi.places.getPlace(originId),
      integrationInstancesServer.junctionMobileApi.places.getPlace(destinationId),
    ]);

    return { origin, destination };
  } catch {
    return {};
  }
}

export function getPassengers(event: RequestEvent): PassengerCountModel {
  return {
    adults: Number(event.url.searchParams.get("adults") ?? 1),
    children: Number(event.url.searchParams.get("children") ?? 0),
    infants: Number(event.url.searchParams.get("infants") ?? 0),
  };
}

export function parsePassengers(
  passengers: PassengerCountModel,
): TripCandidatesModel["passengers"] {
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
