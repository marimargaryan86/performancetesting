import type { CoordinatesModel, PlaceModel } from "models/booking/location";
import type { CoordinatesSchema, PlaceSchema } from "../schemas/place";

export function parseCoordinatesSchema(data: CoordinatesSchema): CoordinatesModel {
  return {
    lat: data.latitude,
    lon: data.longitude,
  };
}

export function parseCoordinatesModel(data: CoordinatesModel): CoordinatesSchema {
  return {
    latitude: data.lat,
    longitude: data.lon,
  };
}

export function parsePlaceSchema(data: PlaceSchema): PlaceModel {
  return {
    id: data.id,
    types: data.relationships?.types.data.map((type) => type.id) ?? [],
    name: data.attributes.name,
    coordinates: parseCoordinatesSchema(data.attributes),
    country: {
      code: data.attributes.countryCode,
      name: data.attributes.countryName ?? undefined,
    },
    timeZone: data.attributes.timeZone,
    iataCode: data.attributes.iataCode?.length ? data.attributes.iataCode : undefined,
  };
}
