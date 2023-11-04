import {
  coordinatesParser,
  type Coordinates,
  type CoordinatesSchema,
} from "integration/common/schemas/point";

export type PlaceType =
  | "unspecified"
  | "city"
  | "railway-station"
  | "airport"
  | "bus-station"
  | "ferry-port";

export type PlaceTypeSchema = {
  id: "unspecified" | "city" | "railway-station" | "airport" | "bus-station" | "ferry-port";
  type: "place-types";
};

export const placeTypeParser = {
  toModel: (data: PlaceTypeSchema): PlaceType => data.id,
};

export type Place = {
  id: string;
  types: PlaceType[];
  name: string;
  coordinates: Coordinates;
  country: {
    code: string;
    name?: string;
  };
  timeZone: string;
  iataCode?: string;
  population?: number;
  mainCity?: string;
};

export type PlaceSchema = {
  id: string;
  type: "places";
  attributes: CoordinatesSchema & {
    name: string;
    countryCode: string;
    countryName?: string;
    timeZone: string;
    iataCode?: string;
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
    iataCode: data.attributes.iataCode,
    population: data.attributes.population,
    mainCity: data.attributes.mainCity,
  }),
};
