import type { TripCandidatesModel } from "models/booking/trip";
import type { CreateTripCandidatesModel } from "../models/trip";
import type {
  CreateTripCandidatesSearchRequestSchema,
  CreateTripCandidatesSearchResponseSchema,
  GetTripCandidatesSearchResponseSchema,
  ListTripCandidatesOffersResponseSchema,
} from "../schemas/trip";
import { parseCoordinatesModel, parseCoordinatesSchema } from "./place";
import type { OfferModel } from "models/booking/offer";
import {
  parseCabinClassSchema,
  parseLegTypeSchema,
  parseOfferGroupDetailsSchema,
  parseOfferGroupSchema,
  parseOfferOptionDetailsSchema,
  parseOfferOptionSchema,
  parseOfferSchema,
} from "./offer";
import type {
  OfferGroupSchema,
  OfferOptionSchema,
  TripOfferGroupDetailsSchema,
  TripOfferOptionDetailsSchema,
} from "../schemas/offer";
import type {
  CabinClassSchema,
  LegTypeSchema,
} from "integration/junction-client-api/schemas/offer";

export function parseCreateTripCandidatesSearchModel(
  data: CreateTripCandidatesModel,
): CreateTripCandidatesSearchRequestSchema {
  return {
    data: {
      type: "trip-candidate-searches",
      attributes: {
        criteria: data.criteria.map((item) => ({
          departureAfter: item.departureAfter.toISOString(),
          destination: parseCoordinatesModel(item.destination),
          origin: parseCoordinatesModel(item.origin),
        })),
        passengers: data.passengers.map((item) => ({
          dateOfBirth: item.dateOfBirth.toLocaleDateString("sv-SE"),
        })),
      },
      relationships: data.allowedLegTypeIds
        ? {
            allowedSegmentTypes: {
              data: data.allowedLegTypeIds.map((id) => ({ id, type: "leg-types" })),
            },
          }
        : undefined,
    },
  };
}

export function parseCreateTripCandidatesSearchResponseSchema(
  data: CreateTripCandidatesSearchResponseSchema,
): TripCandidatesModel {
  return {
    id: data.data.id,
    status: data.data.attributes.status,
    expiresAt: new Date(data.data.attributes.expiresAt),
    criteria: data.data.attributes.criteria.map((item) => ({
      origin: parseCoordinatesSchema(item.origin),
      destination: parseCoordinatesSchema(item.destination),
      departureAfter: new Date(item.departureAfter),
    })),
    passengers: data.data.attributes.passengers.map((item) => ({
      dateOfBirth: new Date(item.dateOfBirth),
    })),
    allowedLegTypeIds: data.data.relationships?.allowedSegmentTypes?.data.map((item) => item.id),
  };
}

export function parseGetTripCandidatesSearchResponseSchema(
  data: GetTripCandidatesSearchResponseSchema,
): TripCandidatesModel {
  return parseCreateTripCandidatesSearchResponseSchema(data);
}

export function parseGetTripCandidatesOffersResponse(
  data: ListTripCandidatesOffersResponseSchema,
): OfferModel[] {
  const legTypes =
    data.included
      ?.filter((item): item is LegTypeSchema => item.type === "leg-types")
      .map(parseLegTypeSchema) ?? [];
  const offerGroupDetails =
    data.included
      ?.filter(
        (item): item is TripOfferGroupDetailsSchema => item.type === "trip-offer-group-details",
      )
      .map((item) => parseOfferGroupDetailsSchema(item, legTypes)) ?? [];
  const cabinClasses =
    data.included
      ?.filter((item): item is CabinClassSchema => item.type === "cabin-classes")
      .map(parseCabinClassSchema) ?? [];
  const offerOptionDetails =
    data.included
      ?.filter(
        (item): item is TripOfferOptionDetailsSchema => item.type === "trip-offer-option-details",
      )
      .map((item) => parseOfferOptionDetailsSchema(item, cabinClasses)) ?? [];
  const offerOptions =
    data.included
      ?.filter((item): item is OfferOptionSchema => item.type === "offer-options")
      .map((item) => parseOfferOptionSchema(item, offerOptionDetails)) ?? [];
  const offerGroups =
    data.included
      ?.filter((item): item is OfferGroupSchema => item.type === "offer-groups")
      .map((item) => parseOfferGroupSchema(item, offerOptions, offerGroupDetails)) ?? [];

  return data.data.map((item) => parseOfferSchema(item, offerGroups));
}
