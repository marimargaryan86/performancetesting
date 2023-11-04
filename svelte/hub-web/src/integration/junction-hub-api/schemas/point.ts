export type Coordinates = {
  lat: number;
  lon: number;
};

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
