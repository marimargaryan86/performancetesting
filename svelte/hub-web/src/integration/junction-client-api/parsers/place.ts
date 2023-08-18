import type { CoordinatesModel } from "models/booking/location";
import type { CoordinatesSchema } from "../schemas/place";

export function parseCoordinatesSchema(data: CoordinatesSchema): CoordinatesModel {
  return {
    lat: data.latitude,
    lon: data.longitude,
  };
}
