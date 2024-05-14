import type { SearchData } from "$lib/booking-manager/booking-manager";
import { z } from "zod";
import * as MobileSchemas from "~/integration/junction-mobile-api/schemas";

export const carSearchDataModel = z
  .object({
    origin: z.object(MobileSchemas.placeModel.shape, {
      required_error: "Pick-up location is required",
    }),
    destination: z.object(MobileSchemas.placeModel.shape, {
      required_error: "Drop-off location is required",
    }),
    pickup: z.date({ required_error: "Pick-up date is required" }),
    dropoff: z.date({ required_error: "Drop-off date is required" }),
    driverAge: z.number({ required_error: "Driver's age is required" }),
  })
  .refine((data) => data.dropoff > data.pickup, {
    message: "Drop-off must be after pick-up",
    path: ["dropoff"],
  });

export type CarSearchData = z.infer<typeof carSearchDataModel>;
export type PartialCarSearchData = Partial<CarSearchData>;
export type CarSearchDataError = z.ZodFormattedError<CarSearchData>;

export const carSearchDataParser = {
  toSearchData: (data: CarSearchData): SearchData => {
    // const today = new Date();

    return {
      origin: data.origin,
      destination: data.destination,
      outbound: data.pickup,
      inbound: data.dropoff,
      passengers: [
        // TODO(2024-05-14/mandersson): Fix when we implement cars
        // new Date(today.getFullYear() - data.driverAge, today.getMonth(), today.getDate()),
      ],
      transportTypes: ["car"],
    };
  },
  fromSearchData: (data: SearchData): CarSearchData => ({
    origin: data.origin,
    destination: data.destination,
    pickup: data.outbound,
    dropoff: data.inbound as Date,
    // TODO(2024-05-14/mandersson): Fix when we implement cars
    driverAge: 25,
    // driverAge: getAge(data.passengers[0] as Date),
  }),
};
