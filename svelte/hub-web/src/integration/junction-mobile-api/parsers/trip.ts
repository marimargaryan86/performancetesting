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
  CabinClassSchema,
  LegTypeSchema,
  OfferGroupSchema,
  OfferOptionSchema,
  TripOfferGroupDetailsSchema,
  TripOfferOptionDetailsSchema,
} from "../schemas/offer";

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
  const legTypes: LegTypeSchema[] = [];
  const offerGroupDetails: TripOfferGroupDetailsSchema[] = [];
  const cabinClasses: CabinClassSchema[] = [];
  const offerOptionDetails: TripOfferOptionDetailsSchema[] = [];
  const offerOptions: OfferOptionSchema[] = [];
  const offerGroups: OfferGroupSchema[] = [];

  data.included?.forEach((item) => {
    if (item.type === "leg-types") {
      legTypes.push(item);
    } else if (item.type === "trip-offer-group-details") {
      offerGroupDetails.push(item);
    } else if (item.type === "cabin-classes") {
      cabinClasses.push(item);
    } else if (item.type === "trip-offer-option-details") {
      offerOptionDetails.push(item);
    } else if (item.type === "offer-options") {
      offerOptions.push(item);
    } else if (item.type === "offer-groups") {
      offerGroups.push(item);
    }
  });

  const legTypes_ = legTypes.map(parseLegTypeSchema);
  const offerGroupDetails_ = offerGroupDetails.map((item) =>
    parseOfferGroupDetailsSchema(item, legTypes_),
  );
  const cabinClasses_ = cabinClasses.map(parseCabinClassSchema);
  const offerOptionDetails_ = offerOptionDetails.map((item) =>
    parseOfferOptionDetailsSchema(item, cabinClasses_),
  );
  const offerOptions_ = offerOptions.map((item) =>
    parseOfferOptionSchema(item, offerOptionDetails_),
  );
  const offerGroups_ = offerGroups.map((item) =>
    parseOfferGroupSchema(item, offerOptions_, offerGroupDetails_),
  );

  return data.data.map((item) => parseOfferSchema(item, offerGroups_));
}
