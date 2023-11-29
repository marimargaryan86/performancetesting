import { writable } from "svelte/store";
import type { OfferSegmentLeg } from "integration/common/schemas/offer-segment-leg";

interface TripStore {
  legs: OfferSegmentLeg[];
  passengersPresentation: string | undefined;
  departureLeg: OfferSegmentLeg | undefined;
  departureDateTime: string | undefined;
  departureStationName: string | undefined;
  arrivalLeg: OfferSegmentLeg | undefined;
  arrivalDateTime: string | undefined;
  arrivalStationName: string | undefined;
}

export const initialTripStore: TripStore = {
  legs: [],
  passengersPresentation: "",
  departureLeg: undefined,
  departureDateTime: "",
  departureStationName: "",
  arrivalLeg: undefined,
  arrivalDateTime: "",
  arrivalStationName: "",
};

export function clearTripStore(): void {
  tripStore.set(initialTripStore);
}

export const tripStore = writable<TripStore>(initialTripStore);
