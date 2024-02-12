import { passengerPickerData } from "./passenger";
import { z } from "zod";
import * as MobileSchemas from "~/integration/junction-mobile-api/schemas";

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

type RequiredFields = keyof Pick<SearchData, "tripType" | "passengers">;
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
export type SearchData = z.infer<typeof searchDataModel>;
export type PartialSearchData = PartialSearchDataOneWay | PartialSearchDataRoundTrip;

export type SearchDataError = z.ZodFormattedError<SearchData>;
