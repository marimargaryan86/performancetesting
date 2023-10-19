import { coordinatesSearchableModel } from "./place";
import { resourceStatus } from "./common";
import { z } from "zod";
import { legTypeModel } from "./offer";
import schemaModel, { type Infer } from "utils/schema-model";

export const tripCandidatesSearchModel = schemaModel.create({
  schema: z.object({
    id: z.string().uuid(),
    type: z.literal("trip-candidate-searches"),
    attributes: z.object({
      expiresAt: z.date({ coerce: true }),
      status: resourceStatus,
      criteria: z.array(
        z.object({
          origin: coordinatesSearchableModel.schema,
          destination: coordinatesSearchableModel.schema,
          departureAfter: z.date({ coerce: true }),
          maximumConnections: z.number().optional(),
        }),
      ),
      passengers: z.array(z.object({ dateOfBirth: z.date({ coerce: true }) })),
    }),
    relationships: schemaModel
      .relationships({
        allowedSegmentTypes: z.array(legTypeModel.identifier).optional(),
      })
      .optional(),
    links: schemaModel.links({ self: true }),
  }),
  model: z.object({
    id: z.string().uuid(),
    expiresAt: z.date({ coerce: true }),
    status: resourceStatus,
    criteria: z.array(
      z.object({
        origin: coordinatesSearchableModel.model,
        destination: coordinatesSearchableModel.model,
        departureAfter: z.date({ coerce: true }),
      }),
    ),
    passengers: z.array(z.object({ dateOfBirth: z.date({ coerce: true }) })),
    allowedLegTypeIds: z.array(z.string()).optional(),
  }),
  toModel: (data) => ({
    id: data.id,
    status: data.attributes.status,
    expiresAt: data.attributes.expiresAt,
    criteria: data.attributes.criteria.map((item) => ({
      origin: coordinatesSearchableModel.toModel(item.origin),
      destination: coordinatesSearchableModel.toModel(item.destination),
      departureAfter: item.departureAfter,
    })),
    passengers: data.attributes.passengers.map((item) => ({
      dateOfBirth: item.dateOfBirth,
    })),
    allowedLegTypeIds: data.relationships?.allowedSegmentTypes?.data.map((item) => item.id),
  }),
});
export type TripCandidatesSearchModel = Infer<typeof tripCandidatesSearchModel>;
export type TripCandidatesSearchSchema = Infer<typeof tripCandidatesSearchModel, "schema">;

export const createTripCandidatesSearchModel = schemaModel.create({
  schema: z.object({
    type: tripCandidatesSearchModel.identifier.shape.type,
    attributes: z.object({
      sessionToken: z.string(),
      criteria: z.array(
        z.object({
          origin: coordinatesSearchableModel.schema,
          destination: coordinatesSearchableModel.schema,
          departureAfter: z.string().datetime(),
          maximumConnections: z.number().optional(),
        }),
      ),
      passengers: z.array(z.object({ dateOfBirth: z.string() })),
    }),
    relationships: schemaModel
      .relationships({
        allowedSegmentTypes: z.array(legTypeModel.identifier).optional(),
      })
      .optional(),
  }),
  model: z.object({
    sessionToken: z.string(),
    criteria: z.array(
      z.object({
        origin: coordinatesSearchableModel.model,
        destination: coordinatesSearchableModel.model,
        departureAfter: z.date({ coerce: true }),
      }),
    ),
    passengers: z.array(z.object({ dateOfBirth: z.date({ coerce: true }) })),
    allowedLegTypeIds: z.array(z.string()).optional(),
  }),
  toSchema: (data) =>
    ({
      type: "trip-candidate-searches",
      attributes: {
        sessionToken: data.sessionToken,
        criteria: data.criteria.map((item) => ({
          departureAfter: item.departureAfter.toISOString(),
          destination: coordinatesSearchableModel.toSchema(item.destination),
          origin: coordinatesSearchableModel.toSchema(item.origin),
        })),
        passengers: data.passengers.map((item) => ({
          dateOfBirth: item.dateOfBirth.toLocaleDateString("sv-SE"),
        })),
      },
      relationships: data.allowedLegTypeIds
        ? {
            allowedSegmentTypes: {
              data: data.allowedLegTypeIds.map((id) => ({ id, type: "leg-types" } as const)),
            },
          }
        : undefined,
    } as const),
});
export type CreateTripCandidatesSearchModel = Infer<typeof createTripCandidatesSearchModel>;
