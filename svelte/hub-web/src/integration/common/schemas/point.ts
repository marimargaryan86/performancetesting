import { z } from "zod";

export const coordinatesSearchableParser = {
  toModel: (data: CoordinatesSearchableSchema): CoordinatesSearchable => ({
    ...coordinatesParser.toModel(data),
    precision: data.precision,
  }),
  toSchema: (data: CoordinatesSearchable): CoordinatesSearchableSchema => ({
    ...coordinatesParser.toSchema(data),
    precision: data.precision,
  }),
};

export const coordinatesModel = z.object({
  lat: z.number(),
  lon: z.number(),
});

export type Coordinates = z.infer<typeof coordinatesModel>;

export type CoordinatesSchema = {
  latitude: number;
  longitude: number;
};

export const coordinatesParser = {
  toModel: (data: CoordinatesSchema): Coordinates => ({
    lat: data.latitude,
    lon: data.longitude,
  }),
  toSchema: (data: Coordinates): CoordinatesSchema => ({
    latitude: data.lat,
    longitude: data.lon,
  }),
};

export type CoordinatesSearchable = Coordinates & {
  precision?: "area" | "precise";
};

export type CoordinatesSearchableSchema = CoordinatesSchema & {
  precision?: "area" | "precise";
};

export const coordinatesSearchableModel = coordinatesModel.extend({
  precision: z.enum(["area", "precise"]).optional(),
});

export type Point = {
  ref: string;
  name: string;
  coordinates: Coordinates;
  timeZone: string;
};

export type PointSchema = CoordinatesSchema & {
  ref: string;
  name: string;
  timeZone: string;
};

export const pointParser = {
  toModel: (data: PointSchema): Point => ({
    ref: data.ref,
    name: data.name,
    coordinates: coordinatesParser.toModel(data),
    timeZone: data.timeZone,
  }),
};
