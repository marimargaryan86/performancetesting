import type { PointModel } from "models/spatial";
import type { PointSchema } from "../schemas/common";
import { parseCoordinatesSchema } from "integration/junction-mobile-api/parsers/place";

export function parsePointSchema(data: PointSchema): PointModel {
  return {
    coordinates: parseCoordinatesSchema(data),
    name: data.name,
    ref: data.ref,
    timeZone: data.timeZone,
  };
}
