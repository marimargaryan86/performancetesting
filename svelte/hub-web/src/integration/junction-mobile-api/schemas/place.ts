import { getSchemaModel, relationship } from "../schema-model.server";
import { z } from "zod";

export const coordinatesModel = getSchemaModel(
  z.object({ latitude: z.number(), longitude: z.number() }),
  z.object({ lat: z.number(), lon: z.number() }),
  {
    toModel: (data) => ({ lat: data.latitude, lon: data.longitude }),
    toSchema: (data) => ({ latitude: data.lat, longitude: data.lon }),
  },
);

export const placeModel = getSchemaModel(
  z.object({
    id: z.string().uuid(),
    type: z.enum(["places"]),
    attributes: z.object({
      name: z.string(),
      latitude: z.number(),
      longitude: z.number(),
      countryCode: z.string(),
      countryName: z.string().nullable().optional(),
      timeZone: z.string(),
      iataCode: z.string().nullable().optional(),
      population: z.number().optional(),
      minCity: z.string().optional(),
    }),
    relationships: relationship({
      types: z.array(z.object({ id: z.string(), type: z.enum(["place-types"]) })),
    }).optional(),
  }),
  z.object({
    id: z.string(),
    types: z.array(z.string()),
    name: z.string(),
    coordinates: coordinatesModel.model,
    timeZone: z.string(),
    iataCode: z.string().optional(),
    country: z.object({
      code: z.string(),
      name: z.string().optional(),
    }),
  }),
  {
    toModel: (data) => ({
      ...data,
      ...data.attributes,
      iataCode: data.attributes.iataCode ?? undefined,
      coordinates: coordinatesModel.toModel(data.attributes),
      types: data.relationships?.types.data.map((item) => item.id) ?? [],
      country: {
        code: data.attributes.countryCode,
        name: data.attributes.countryName ?? undefined,
      },
    }),
  },
);
