import { PASSENGER_DEFINITIONS, passengerPickerData } from "$lib/models/passenger";
import * as MobileSchemas from "~/integration/junction-mobile-api/schemas";
import type { SearchData } from "$lib/booking-manager/booking-manager";
import { z } from "zod";
import { getAge } from "$lib/utils/date-time";

export const TRIP_TYPES = ["one-way", "round-trip"] as const;
export type TripType = (typeof TRIP_TYPES)[number];

export const SEARCH_WINDOW_H = 2;
export const SEARCH_WINDOW_DELTA_MS = 3600000 * SEARCH_WINDOW_H;

const searchDataBaseModel = z.object({
  origin: z.object(MobileSchemas.placeModel.shape, { required_error: "Origin is mandatory" }),
  destination: z.object(MobileSchemas.placeModel.shape, {
    required_error: "Destination is mandatory",
  }),
  passengers: passengerPickerData,
  windowH: z.number().min(0).default(SEARCH_WINDOW_H),
  outbound: z
    .date({ coerce: true, required_error: "Departure date is mandatory" })
    .refine((value) => value >= new Date(), "Departure date can't be in the past"),
});

type RequiredFields = keyof Pick<TripSearchData, "tripType" | "passengers">;
const searchDataOneWayModel = searchDataBaseModel.extend({
  tripType: z.literal("one-way" satisfies TripType),
});
type SearchDataOneWay = z.infer<typeof searchDataOneWayModel>;
type PartialSearchDataOneWay = Partial<Omit<SearchDataOneWay, RequiredFields>> &
  Pick<SearchDataOneWay, RequiredFields>;

const searchDataRoundTripModel = searchDataBaseModel.extend({
  tripType: z.literal("round-trip" satisfies TripType),
  outbound: z
    .date({ coerce: true, required_error: "Outbound date is mandatory" })
    .refine((value) => value > new Date(), "Outbound date can't be in the past"),
  inbound: z.date({ coerce: true, required_error: "Inbound date is mandatory" }),
});
type SearchDataRoundTrip = z.infer<typeof searchDataRoundTripModel>;
type PartialSearchDataRoundTrip = Partial<Omit<SearchDataRoundTrip, RequiredFields>> &
  Pick<SearchDataRoundTrip, RequiredFields>;

export const searchDataModel = z
  .discriminatedUnion("tripType", [searchDataOneWayModel, searchDataRoundTripModel])
  .refine((value) => value.tripType !== "round-trip" || value.inbound > value.outbound, {
    message: "Inbound date must be after outbound date",
    path: ["inbound"],
  });
export type TripSearchData = z.infer<typeof searchDataModel>;
export type PartialTripSearchData = PartialSearchDataOneWay | PartialSearchDataRoundTrip;
export type TripSearchDataError = z.ZodFormattedError<TripSearchData>;

function getBirthDate(age: number): Date {
  const date = new Date();
  date.setFullYear(date.getFullYear() - age);

  return date;
}

function getBirthDates(): Record<keyof typeof PASSENGER_DEFINITIONS, Date> {
  return {
    adults: getBirthDate(PASSENGER_DEFINITIONS.adults.span.from),
    children0: getBirthDate(PASSENGER_DEFINITIONS.children0.span.from),
    children4: getBirthDate(PASSENGER_DEFINITIONS.children0.span.from),
    children6: getBirthDate(PASSENGER_DEFINITIONS.children6.span.from),
    seniors60: getBirthDate(PASSENGER_DEFINITIONS.seniors60.span.from),
    seniors65: getBirthDate(PASSENGER_DEFINITIONS.seniors65.span.from),
    youths12: getBirthDate(PASSENGER_DEFINITIONS.youths12.span.from),
    youths15: getBirthDate(PASSENGER_DEFINITIONS.youths15.span.from),
  };
}

function getPassengerCount(ages: number[], min: number, max: number): number {
  return ages.filter((age) => age < max && age >= min).length;
}

export const passengerParser = {
  toSearchData: (data: TripSearchData["passengers"]): Date[] => {
    const birthDates = getBirthDates();

    return [
      ...Array.from(Array(data.adults), () => new Date(birthDates.adults)),
      ...Array.from(Array(data.children0), () => new Date(birthDates.children0)),
      ...Array.from(Array(data.children4), () => new Date(birthDates.children4)),
      ...Array.from(Array(data.children6), () => new Date(birthDates.children6)),
      ...Array.from(Array(data.seniors60), () => new Date(birthDates.seniors60)),
      ...Array.from(Array(data.seniors65), () => new Date(birthDates.seniors65)),
      ...Array.from(Array(data.youths12), () => new Date(birthDates.youths12)),
      ...Array.from(Array(data.youths15), () => new Date(birthDates.youths15)),
    ];
  },
  fromSearchData: (data: Date[]): TripSearchData["passengers"] => {
    const ages = data.map((date) => getAge(date));

    return {
      adults: getPassengerCount(
        ages,
        PASSENGER_DEFINITIONS.adults.span.from,
        PASSENGER_DEFINITIONS.seniors60.span.from,
      ),
      children0: getPassengerCount(
        ages,
        PASSENGER_DEFINITIONS.children0.span.from,
        PASSENGER_DEFINITIONS.children4.span.from,
      ),
      children4: getPassengerCount(
        ages,
        PASSENGER_DEFINITIONS.children4.span.from,
        PASSENGER_DEFINITIONS.children6.span.from,
      ),
      children6: getPassengerCount(
        ages,
        PASSENGER_DEFINITIONS.children6.span.from,
        PASSENGER_DEFINITIONS.youths12.span.from,
      ),
      seniors60: getPassengerCount(
        ages,
        PASSENGER_DEFINITIONS.seniors60.span.from,
        PASSENGER_DEFINITIONS.seniors65.span.from,
      ),
      seniors65: getPassengerCount(
        ages,
        PASSENGER_DEFINITIONS.seniors65.span.from,
        Number.MAX_SAFE_INTEGER,
      ),
      youths12: getPassengerCount(
        ages,
        PASSENGER_DEFINITIONS.youths12.span.from,
        PASSENGER_DEFINITIONS.youths15.span.from,
      ),
      youths15: getPassengerCount(
        ages,
        PASSENGER_DEFINITIONS.youths15.span.from,
        PASSENGER_DEFINITIONS.adults.span.from,
      ),
    };
  },
};

export const tripSearchDataParser = {
  toSearchData: (data: TripSearchData): SearchData => ({
    origin: data.origin,
    destination: data.destination,
    outbound: data.outbound,
    inbound: data.tripType === "round-trip" ? data.inbound : undefined,
    passengers: passengerParser.toSearchData(data.passengers),
    transportTypes: ["rail"],
    windowH: data.windowH,
  }),
  fromSearchData: (data: SearchData): TripSearchData => {
    const base: Omit<TripSearchData, "inbound" | "tripType"> = {
      origin: data.origin,
      destination: data.destination,
      outbound: data.outbound,
      passengers: passengerParser.fromSearchData(data.passengers),
      windowH: data.windowH ?? SEARCH_WINDOW_H,
    };

    if (data.inbound) {
      return {
        ...base,
        tripType: "round-trip",
        inbound: data.inbound,
      };
    }

    return {
      ...base,
      tripType: "one-way",
    };
  },
};
