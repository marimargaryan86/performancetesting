import { z } from "zod";
import { getSchemaModel, type Infer } from "../../common/schema-model.server";
import { coordinatesModel } from "./place";

export const pointModel = getSchemaModel(
  z.object({
    ref: z.string(),
    name: z.string(),
    latitude: z.number(),
    longitude: z.number(),
    timeZone: z.string(),
  }),
  z.object({
    coordinates: coordinatesModel.model,
    name: z.string(),
    ref: z.string(),
    timeZone: z.string(),
  }),
  {
    toModel: (data) => ({
      ...data,
      coordinates: coordinatesModel.toModel(data),
    }),
    toSchema: (data) => ({
      ...data,
      ...coordinatesModel.toSchema(data.coordinates),
    }),
  },
);
export type PointModel = Infer<typeof pointModel>;

export const resourceStatuses = [
  "unspecified",
  "pending",
  "processing",
  "completed",
  "failed",
] as const;
export const resourceStatus = z.enum(resourceStatuses);
export type ResourceStatus = z.infer<typeof resourceStatus>;
