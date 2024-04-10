import * as CommonSchemas from "~/integration/common/schemas";
import { z } from "zod";
import type { Specification } from "./__generated__";
import type { GetOKResponse } from "~/integration/common/types";

const placeType = z.enum([
  "unspecified",
  "city",
  "railway-station",
  "airport",
  "bus-station",
  "ferry-port",
]);

export type PlaceType = z.infer<typeof placeType>;

export type PlaceTypeSchema = {
  id: string;
  type: "place-types";
};

export const placeTypeParser = {
  toModel: (data: PlaceTypeSchema): PlaceType => data.id as PlaceType,
};

export const placeModel = z.object({
  id: z.string(),
  types: z.array(placeType),
  name: z.string(),
  coordinates: CommonSchemas.coordinatesModel,
  country: z.object({
    code: z.string(),
    name: z.string().optional(),
  }),
  timeZone: z.string(),
  iataCode: z.string().optional(),
  population: z.number().optional(),
  mainCity: z.string().optional(),
});

export type Place = z.infer<typeof placeModel>;

export type PlaceSchema = GetOKResponse<Specification, "/places">["data"][number];

export const placeParser = {
  toModel: (data: PlaceSchema): Place => {
    if (!(data.id && data.relationships && data.attributes && data.attributes.countryName)) {
      throw new Error("Poorly formatted place");
    }

    return {
      id: data.id,
      types: data.relationships.types.data.map(placeTypeParser.toModel),
      name: data.attributes.name,
      coordinates: CommonSchemas.coordinatesParser.toModel(data.attributes),
      country: {
        code: data.attributes.countryCode,
        name: data.attributes.countryName,
      },
      timeZone: data.attributes.timeZone,
      iataCode: data.attributes.iataCode ?? undefined,
      population: data.attributes.population,
      mainCity: data.attributes.mainCity?.length ? data.attributes.mainCity : undefined,
    };
  },
};
