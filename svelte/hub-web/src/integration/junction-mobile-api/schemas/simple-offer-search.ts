import {
  coordinatesParser,
  type Coordinates,
  type CoordinatesSchema,
} from "integration/common/schemas/point";
import type { TripCandidateSearch, TripCandidateSearchSchema } from "./trip-candidate";
import { tripOfferPassengerParser } from "./offer-search";

export type SimpleOfferSearchCriteria = {
  origin: Coordinates;
  destination: Coordinates;
  departureAfter: Date;
};

export type SimpleOfferSearchCriteriaSchema = {
  origin: CoordinatesSchema;
  destination: CoordinatesSchema;
  departureAfter: string;
};

export const simpleOfferSearchCriteriaParser = {
  toModel: (data: SimpleOfferSearchCriteriaSchema): SimpleOfferSearchCriteria => ({
    origin: coordinatesParser.toModel(data.origin),
    destination: coordinatesParser.toModel(data.destination),
    departureAfter: new Date(data.departureAfter),
  }),
  toSchema: (data: SimpleOfferSearchCriteria): SimpleOfferSearchCriteriaSchema => ({
    origin: coordinatesParser.toSchema(data.origin),
    destination: coordinatesParser.toSchema(data.destination),
    departureAfter: data.departureAfter.toISOString(),
  }),
};

export type SimpleOfferSearch = Omit<TripCandidateSearch, "criteria"> & {
  criteria: SimpleOfferSearchCriteria;
};

export type SimpleOfferSearchSchema = Omit<TripCandidateSearchSchema, "type" | "attributes"> & {
  type: "simple-offer-searches";
  attributes: Omit<TripCandidateSearchSchema["attributes"], "criteria"> & {
    criteria: SimpleOfferSearchCriteriaSchema;
  };
};

export type SimpleOfferSearchCreate = Pick<
  SimpleOfferSearch,
  "criteria" | "passengers" | "allowedSegmentTypes"
> & {
  sessionToken?: string;
};

export type SimpleOfferSearchCreateSchema = Pick<SimpleOfferSearchSchema, "relationships"> &
  Pick<SimpleOfferSearchSchema, "type"> & {
    attributes: Pick<SimpleOfferSearchSchema["attributes"], "criteria" | "passengers"> & {
      sessionToken?: string;
    };
  };

export const simpleOffserSearchParser = {
  toModel: (data: SimpleOfferSearchSchema): SimpleOfferSearch => ({
    id: data.id,
    status: data.attributes.status,
    expiresAt: new Date(data.attributes.expiresAt),
    passengers: data.attributes.passengers.map(tripOfferPassengerParser.toModel),
    allowedSegmentTypes: data.relationships?.allowedSegmentTypes?.data.map(({ id }) => id) ?? [],
    criteria: simpleOfferSearchCriteriaParser.toModel(data.attributes.criteria),
  }),
  toCreateSchema: (data: SimpleOfferSearchCreate): SimpleOfferSearchCreateSchema => ({
    type: "simple-offer-searches",
    attributes: {
      sessionToken: data.sessionToken,
      criteria: simpleOfferSearchCriteriaParser.toSchema(data.criteria),
      passengers: data.passengers.map(tripOfferPassengerParser.toSchema),
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
