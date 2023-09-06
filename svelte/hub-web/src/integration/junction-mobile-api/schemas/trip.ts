import { coordinatesModel } from "./place";
import { resourceStatus } from "./common";
import { getSchemaModel, links, relationship, type Infer } from "../schema-model.server";
import { z } from "zod";

export const tripCandidatesSearchModel = getSchemaModel(
  z.object({
    id: z.string().uuid(),
    type: z.enum(["trip-candidate-searches"]),
    attributes: z.object({
      expiresAt: z.date({ coerce: true }),
      status: resourceStatus,
      criteria: z.array(
        z.object({
          origin: coordinatesModel.schema,
          destination: coordinatesModel.schema,
          departureAfter: z.date({ coerce: true }),
          maximumConnections: z.number().optional(),
        }),
      ),
      passengers: z.array(z.object({ dateOfBirth: z.date({ coerce: true }) })),
    }),
    relationships: relationship({
      allowedSegmentTypes: z
        .array(
          z.object({
            id: z.string(),
            type: z.enum(["leg-types"]),
          }),
        )
        .optional(),
    }).optional(),
    links: links(["self"]),
  }),
  z.object({
    id: z.string().uuid(),
    expiresAt: z.date({ coerce: true }),
    status: resourceStatus,
    criteria: z.array(
      z.object({
        origin: coordinatesModel.model,
        destination: coordinatesModel.model,
        departureAfter: z.date({ coerce: true }),
      }),
    ),
    passengers: z.array(z.object({ dateOfBirth: z.date({ coerce: true }) })),
    allowedLegTypeIds: z.array(z.string()).optional(),
  }),
  {
    toModel: (data) => ({
      id: data.id,
      status: data.attributes.status,
      expiresAt: data.attributes.expiresAt,
      criteria: data.attributes.criteria.map((item) => ({
        origin: coordinatesModel.toModel(item.origin),
        destination: coordinatesModel.toModel(item.destination),
        departureAfter: item.departureAfter,
      })),
      passengers: data.attributes.passengers.map((item) => ({
        dateOfBirth: item.dateOfBirth,
      })),
      allowedLegTypeIds: data.relationships?.allowedSegmentTypes?.data.map((item) => item.id),
    }),
  },
);
export type TripCandidatesSearchModel = Infer<typeof tripCandidatesSearchModel>;
export type TripCandidatesSearchSchema = Infer<typeof tripCandidatesSearchModel, "schema">;

export const createTripCandidatesSearchModel = getSchemaModel(
  tripCandidatesSearchModel.schema.omit({ links: true, id: true }).extend({
    attributes: tripCandidatesSearchModel.schema.shape.attributes
      .omit({ expiresAt: true, status: true })
      .extend({
        sessionToken: z.string(),
        criteria: z.array(
          tripCandidatesSearchModel.schema.shape.attributes.shape.criteria.element.extend({
            departureAfter: z.string(),
          }),
        ),
        passengers: z.array(z.object({ dateOfBirth: z.string() })),
      }),
  }),
  z.object({
    sessionToken: z.string(),
    criteria: z.array(
      z.object({
        origin: coordinatesModel.model,
        destination: coordinatesModel.model,
        departureAfter: z.date({ coerce: true }),
      }),
    ),
    passengers: z.array(z.object({ dateOfBirth: z.date({ coerce: true }) })),
    allowedLegTypeIds: z.array(z.string()).optional(),
  }),
  {
    toSchema: (data) => ({
      type: "trip-candidate-searches" as const,
      attributes: {
        sessionToken: data.sessionToken,
        criteria: data.criteria.map((item) => ({
          departureAfter: item.departureAfter.toISOString(),
          destination: coordinatesModel.toSchema(item.destination),
          origin: coordinatesModel.toSchema(item.origin),
        })),
        passengers: data.passengers.map((item) => ({
          dateOfBirth: item.dateOfBirth.toLocaleDateString("sv-SE"),
        })),
      },
      relationships: data.allowedLegTypeIds
        ? {
            allowedSegmentTypes: {
              data: data.allowedLegTypeIds.map((id) => ({ id, type: "leg-types" as const })),
            },
          }
        : undefined,
    }),
  },
);
export type CreateTripCandidatesSearchModel = Infer<typeof createTripCandidatesSearchModel>;
export type CreateTripCandidatesSearchSchema = Infer<
  typeof createTripCandidatesSearchModel,
  "schema"
>;
