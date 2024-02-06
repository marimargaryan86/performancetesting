import {
  coordinatesSearchableParser,
  type CoordinatesSearchable,
  type CoordinatesSearchableSchema,
} from "~/integration/common/schemas/point";
import {
  tripOfferPassengerParser,
  type TripOfferPassenger,
  type TripOfferPassengerSchema,
} from "./offer-search";
import type { LegType, LegTypeSchema } from "~/integration/common/schemas/leg-type";

export type TripCandidateSearchCriteria = {
  origin: CoordinatesSearchable;
  destination: CoordinatesSearchable;
  departureAfter: Date;
  departureBefore?: Date;
  maximumConnections?: number;
};

export type TripCandidateSearchCriteriaSchema = {
  origin: CoordinatesSearchableSchema;
  destination: CoordinatesSearchableSchema;
  departureAfter: string;
  departureBefore?: string;
  maximumConnections?: number;
};

export const tripCandidateSearchCriteriaParser = {
  toModel: (data: TripCandidateSearchCriteriaSchema): TripCandidateSearchCriteria => ({
    origin: coordinatesSearchableParser.toModel(data.origin),
    destination: coordinatesSearchableParser.toModel(data.destination),
    departureAfter: new Date(data.departureAfter),
    departureBefore: data.departureBefore ? new Date(data.departureBefore) : undefined,
    maximumConnections: data.maximumConnections,
  }),
  toSchema: (data: TripCandidateSearchCriteria): TripCandidateSearchCriteriaSchema => ({
    origin: coordinatesSearchableParser.toSchema(data.origin),
    destination: coordinatesSearchableParser.toSchema(data.destination),
    departureAfter: data.departureAfter.toISOString(),
    departureBefore: data.departureBefore?.toISOString(),
    maximumConnections: data.maximumConnections,
  }),
};

export type TripCandidateSearch = {
  id: string;
  expiresAt: Date;
  status: "unspecified" | "pending" | "processing" | "completed" | "failed";
  criteria: TripCandidateSearchCriteria[];
  passengers: TripOfferPassenger[];
  allowedSegmentTypes?: LegType["id"][];
};

export type TripCandidateSearchSchema = {
  id: string;
  type: "trip-candidate-searches";
  attributes: {
    expiresAt: string;
    status: "unspecified" | "pending" | "processing" | "completed" | "failed";
    criteria: TripCandidateSearchCriteriaSchema[];
    passengers: TripOfferPassengerSchema[];
  };
  relationships?: {
    allowedSegmentTypes?: { data: Pick<LegTypeSchema, "id" | "type">[] };
  };
  links: { self: string };
};

export type TripCandidateSearchCreate = Pick<
  TripCandidateSearch,
  "criteria" | "passengers" | "allowedSegmentTypes"
> & {
  sessionToken?: string;
};

export type TripCandidateSearchCreateSchema = Pick<
  TripCandidateSearchSchema,
  "type" | "relationships"
> & {
  attributes: Pick<TripCandidateSearchSchema["attributes"], "criteria" | "passengers"> & {
    sessionToken?: string;
  };
};

export const tripCandidateSearchParser = {
  toModel: (data: TripCandidateSearchSchema): TripCandidateSearch => ({
    id: data.id,
    expiresAt: new Date(data.attributes.expiresAt),
    status: data.attributes.status,
    criteria: data.attributes.criteria.map(tripCandidateSearchCriteriaParser.toModel),
    passengers: data.attributes.passengers.map(tripOfferPassengerParser.toModel),
    allowedSegmentTypes: data.relationships?.allowedSegmentTypes?.data.map(({ id }) => id),
  }),
  toCreateSchema: (data: TripCandidateSearchCreate): TripCandidateSearchCreateSchema => ({
    type: "trip-candidate-searches",
    attributes: {
      criteria: data.criteria.map(tripCandidateSearchCriteriaParser.toSchema),
      passengers: data.passengers.map(tripOfferPassengerParser.toSchema),
      sessionToken: data.sessionToken,
    },
    relationships: data.allowedSegmentTypes
      ? {
          allowedSegmentTypes: {
            data: data.allowedSegmentTypes.map((id) => ({ id, type: "leg-types" })),
          },
        }
      : undefined,
  }),
};
