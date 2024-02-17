import { sleep } from "$lib/utils/common";
import { z } from "zod";
import * as MobileSchemas from "~/integration/junction-mobile-api/schemas";

const carSearchDataSameLocationModel = z.object({
  origin: MobileSchemas.placeModel,
  pickup: z.date(),
  dropoff: z.date(),
  driver25to65: z.boolean().default(false),
  driversAge: z.number().nullable().optional(),
});

const carSearchDataDifferentLocationModel = carSearchDataSameLocationModel.extend({
  destination: MobileSchemas.placeModel,
});

type CarSearchDataParser = z.ZodEffects<
  typeof carSearchDataSameLocationModel | typeof carSearchDataDifferentLocationModel
>;

export function getSearchDataModel(dropoffSameLocation: boolean): CarSearchDataParser {
  return (
    dropoffSameLocation ? carSearchDataSameLocationModel : carSearchDataDifferentLocationModel
  ).refine(
    (value) => value.driver25to65 || (value.driversAge !== undefined && value.driversAge !== null),
    {
      message: "Please specify the driver's age",
      path: ["driversAge"],
    },
  );
}

export type CarSearchData = z.infer<CarSearchDataParser>;
export type CarSearchErrors = z.ZodFormattedError<CarSearchData>;
export type PartialCarSearchData =
  | ({ dropoffDifferentLocation: false } & Partial<z.infer<typeof carSearchDataSameLocationModel>>)
  | ({ dropoffDifferentLocation: true; destination?: MobileSchemas.Place } & Partial<
      z.infer<typeof carSearchDataSameLocationModel>
    >);

// eslint-disable-next-line @typescript-eslint/no-unused-vars
async function search(data: CarSearchData): Promise<void> {
  // TODO: Impl.
  await sleep(2000);
}

export const manager = {
  search,
};
