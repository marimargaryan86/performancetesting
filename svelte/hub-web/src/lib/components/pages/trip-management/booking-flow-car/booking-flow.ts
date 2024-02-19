import { sleep } from "$lib/utils/common";
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

// eslint-disable-next-line @typescript-eslint/no-unused-vars
async function search(data: CarSearchData): Promise<void> {
  // TODO: Impl.
  await sleep(2000);
}

export const manager = {
  search,
};
