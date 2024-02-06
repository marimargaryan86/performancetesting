import {
  coordinatesParser,
  type CoordinatesSchema,
  coordinatesModel,
} from "~/integration/common/schemas/point";
import { z } from "zod";

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
  id: "unspecified" | "city" | "railway-station" | "airport" | "bus-station" | "ferry-port";
  type: "place-types";
};

export const placeTypeParser = {
  toModel: (data: PlaceTypeSchema): PlaceType => data.id,
};

export const placeModel = z.object({
  id: z.string(),
  types: z.array(placeType),
  name: z.string(),
  coordinates: coordinatesModel,
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

export type PlaceSchema = {
  id: string;
  type: "places";
  attributes: CoordinatesSchema & {
    name: string;
    countryCode: string;
    countryName?: string;
    timeZone: string;
    iataCode?: string | null;
    population?: number;
    mainCity?: string;
  };
  relationships: {
    types: { data: Pick<PlaceTypeSchema, "id" | "type">[] };
  };
};

export const placeParser = {
  toModel: (data: PlaceSchema): Place => ({
    id: data.id,
    types: data.relationships.types.data.map(placeTypeParser.toModel),
    name: data.attributes.name,
    coordinates: coordinatesParser.toModel(data.attributes),
    country: {
      code: data.attributes.countryCode,
      name: data.attributes.countryName,
    },
    timeZone: data.attributes.timeZone,
    iataCode: data.attributes.iataCode ?? undefined,
    population: data.attributes.population,
    mainCity: data.attributes.mainCity?.length ? data.attributes.mainCity : undefined,
  }),
};
