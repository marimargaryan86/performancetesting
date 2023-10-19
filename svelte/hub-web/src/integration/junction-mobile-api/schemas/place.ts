import schemaModel, { type Infer } from "utils/schema-model";
import { z } from "zod";

export const coordinatesModel = schemaModel.create({
  schema: z.object({ latitude: z.number(), longitude: z.number() }),
  model: z.object({ lat: z.number(), lon: z.number() }),
  toModel: (data) => ({ lat: data.latitude, lon: data.longitude }),
  toSchema: (data) => ({ latitude: data.lat, longitude: data.lon }),
});

export const coordinatesSearchableModel = schemaModel.create({
  schema: coordinatesModel.schema.extend({
    precision: z.enum(["area", "precise"]).optional(),
  }),
  model: coordinatesModel.model.extend({
    precision: z.enum(["area", "precise"]).optional(),
  }),
  toModel: (data) => ({
    ...coordinatesModel.toModel(data),
    precision: data.precision,
  }),
  toSchema: (data) => ({
    ...coordinatesModel.toSchema(data),
    precision: data.precision,
  }),
});

export const placeModel = schemaModel.create({
  schema: z.object({
    id: z.string().uuid(),
    type: z.literal("places"),
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
    relationships: schemaModel
      .relationships({
        types: z.array(z.object({ id: z.string(), type: z.literal("place-types") })),
      })
      .optional(),
  }),
  model: z.object({
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
});
export type PlaceModel = Infer<typeof placeModel>;
export type PlaceSchema = Infer<typeof placeModel, "schema">;
