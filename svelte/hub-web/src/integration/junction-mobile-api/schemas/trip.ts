import type { RelationshipSchema } from "integration/common/schemas";
import type { CoordinatesSchema } from "./place";
import type {
  OfferGroupSchema,
  OfferOptionSchema,
  TripOfferSchema,
  TripOfferGroupDetailsSchema,
  TripOfferOptionDetailsSchema,
  LegTypeIdentifierSchema,
  LegTypeSchema,
  CabinClassSchema,
} from "./offer";

export type TripSearchStatus = "unspecified" | "pending" | "processing" | "completed" | "failed";

export type TripCandidatesSearchStatus =
  | "unspecified"
  | "pending"
  | "processing"
  | "completed"
  | "failed";

export interface TripCandidatesSearchSchema {
  id: string;
  type: "trip-candidate-searches";
  attributes: {
    expiresAt: string;
    status: TripCandidatesSearchStatus;
    criteria: {
      origin: CoordinatesSchema;
      destination: CoordinatesSchema;
      departureAfter: string;
      maximumConnections?: number;
    }[];
    passengers: { dateOfBirth: string }[];
  };
  relationships?: {
    allowedSegmentTypes?: RelationshipSchema<LegTypeIdentifierSchema[]>;
  };
  links: { self: string };
}

export interface CreateTripCandidatesSearchRequestSchema {
  data: Omit<TripCandidatesSearchSchema, "id" | "attributes" | "links"> & {
    attributes: Omit<TripCandidatesSearchSchema["attributes"], "expiresAt" | "status"> & {
      sessionToken: string;
    };
  };
}

export interface CreateTripCandidatesSearchResponseSchema {
  data: TripCandidatesSearchSchema;
}

export interface GetTripCandidatesSearchResponseSchema {
  data: TripCandidatesSearchSchema;
}

export interface ListTripCandidatesOffersResponseSchema {
  data: TripOfferSchema[];
  included?: (
    | OfferGroupSchema
    | TripOfferGroupDetailsSchema
    | LegTypeSchema
    | OfferOptionSchema
    | TripOfferOptionDetailsSchema
    | CabinClassSchema
  )[];
  links: { next: string };
}
