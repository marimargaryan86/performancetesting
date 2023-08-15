import type { RelationshipSchema } from "integration/common/schemas";

export interface CoordinatesSchema {
  latitude: number;
  longitude: number;
}

export interface PlaceIdentifierSchema {
  id: string;
  type: "places";
}

export interface PlaceTypeIdentifier {
  id: string;
  type: "place-types";
}

export interface PlaceSchema extends PlaceIdentifierSchema {
  attributes: {
    name: string;
    latitude: number;
    longitude: number;
    countryCode: string;
    countryName?: string | null;
    timeZone: string;
    iataCode?: string | null;
    population?: number;
    minCity?: string;
  };
  relationships?: {
    types: RelationshipSchema<PlaceTypeIdentifier[]>;
  };
}

export interface ListPlacesResponseSchema {
  data: PlaceSchema[];
}

export interface GetPlaceResponseSchema {
  data: PlaceSchema;
}
