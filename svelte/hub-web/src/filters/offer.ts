import { getTimeOfDayM } from "~/utils/date-time";
import {
  getMinStopCount,
  getEarliestDeparture,
  getEarliestArrival,
  getOfferDurationM,
} from "~/utils/offer";
import type { SearchOptionsData } from "../routes/trip-management/book/train/select-offer/search-options.svelte";
import type { Offer } from "~/integration/junction-mobile-api/schemas/offer";

function stopsFulfilled(options: SearchOptionsData, offer: Offer): boolean {
  if (options.stops.includes("direct") && getMinStopCount(offer) > 1) {
    return false;
  }

  return true;
}

function departureFulfilled(options: SearchOptionsData, offer: Offer): boolean {
  const departureTime = getTimeOfDayM(getEarliestDeparture(offer));

  return (
    options.departureSpanM.start <= departureTime && departureTime <= options.departureSpanM.end
  );
}

function arrivalFulfilled(options: SearchOptionsData, offer: Offer): boolean {
  const arrivalTime = getTimeOfDayM(getEarliestArrival(offer));

  return options.arrivalSpanM.start <= arrivalTime && arrivalTime <= options.arrivalSpanM.end;
}

function durationFulfilled(options: SearchOptionsData, offer: Offer): boolean {
  const duration = getOfferDurationM(offer);

  return options.durationM <= duration;
}

function vendorsFulfilled(options: SearchOptionsData, offer: Offer): boolean {
  if (!options.vendors.length) {
    return true;
  }

  const vendors = offer.groups.flatMap((group) =>
    group.detailsList.map((details) => details.vendor),
  );

  return Boolean(options.vendors.find((item: string) => vendors.includes(item)));
}

export function getFilterOffersFunc(options: SearchOptionsData): (offer: Offer) => boolean {
  return (offer: Offer): boolean => {
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
