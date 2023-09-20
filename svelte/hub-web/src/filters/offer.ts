import { getTimeOfDayM } from "utils/date-time";
import {
  getMinStopCount,
  getEarliestDeparture,
  getEarliestArrival,
  getOfferDurationM,
} from "utils/offer";
import type { SearchOptionsData } from "../routes/trip-management/book/select-offer/search-options.svelte";
import type { OfferModel } from "integration/junction-mobile-api/schemas/offer";

function stopsFulfilled(options: SearchOptionsData, offer: OfferModel): boolean {
  if (options.stops.includes("direct") && getMinStopCount(offer) > 1) {
    return false;
  }

  return true;
}

function departureFulfilled(options: SearchOptionsData, offer: OfferModel): boolean {
  const departureTime = getTimeOfDayM(getEarliestDeparture(offer));

  return (
    options.departureSpanM.start <= departureTime && departureTime <= options.departureSpanM.end
  );
}

function arrivalFulfilled(options: SearchOptionsData, offer: OfferModel): boolean {
  const arrivalTime = getTimeOfDayM(getEarliestArrival(offer));

  return options.arrivalSpanM.start <= arrivalTime && arrivalTime <= options.arrivalSpanM.end;
}

function durationFulfilled(options: SearchOptionsData, offer: OfferModel): boolean {
  const duration = getOfferDurationM(offer);

  return options.durationM <= duration;
}

function vendorsFulfilled(options: SearchOptionsData, offer: OfferModel): boolean {
  if (!options.vendors.length) {
    return true;
  }

  const vendors = offer.groups.flatMap((group) => group.details.map((details) => details.vendor));

  return Boolean(options.vendors.find((item) => vendors.includes(item)));
}

export function getFilterOffersFunc(options: SearchOptionsData): (offer: OfferModel) => boolean {
  return (offer: OfferModel): boolean => {
    const fulfilled = {
      meep: true,
      stops: stopsFulfilled(options, offer),
      departure: departureFulfilled(options, offer),
      arrival: arrivalFulfilled(options, offer),
      duration: durationFulfilled(options, offer),
      operators: vendorsFulfilled(options, offer),
    };

    return Object.values(fulfilled).reduce((prev, curr) => prev && curr);
  };
}
