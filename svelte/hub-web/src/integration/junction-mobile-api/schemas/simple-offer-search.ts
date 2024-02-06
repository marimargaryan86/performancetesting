import {
  coordinatesParser,
  type Coordinates,
  type CoordinatesSchema,
} from "~/integration/common/schemas/point";
import type { TripCandidateSearch, TripCandidateSearchSchema } from "./trip-candidate";
import { tripOfferPassengerParser } from "./offer-search";

export type SimpleOfferSearchCriteria = {
  origin: Coordinates;
  destination: Coordinates;
  outbound: Date;
  inbound?: Date;
  windowH?: number;
};

export type SimpleOfferSearchCriteriaSchema = {
  origin: CoordinatesSchema;
  destination: CoordinatesSchema;
  departureAfter: string;
  departureBefore?: string | null;
  arrivalBefore?: string | null;
  returnDepartureBefore?: string | null;
  returnDepartureAfter?: string | null;
};

export const simpleOfferSearchCriteriaParser = {
  toModel: (data: SimpleOfferSearchCriteriaSchema): SimpleOfferSearchCriteria => {
    const outboundAfter = new Date(data.departureAfter);
    const outboundBefore = data.departureBefore ? new Date(data.departureBefore) : undefined;
    const windowH = outboundBefore
      ? (outboundAfter.getTime() - outboundBefore.getTime()) / 3600000
      : undefined;

    return {
      origin: coordinatesParser.toModel(data.origin),
      destination: coordinatesParser.toModel(data.destination),
      outbound: new Date(data.departureAfter),
      inbound: data.returnDepartureAfter ? new Date(data.returnDepartureAfter) : undefined,
      windowH,
    };
  },
  toSchema: (data: SimpleOfferSearchCriteria): SimpleOfferSearchCriteriaSchema => {
    const outboundAfter = data.outbound;
    const outboundBefore = data.windowH ? new Date(data.outbound) : undefined;
    outboundBefore?.setHours(outboundBefore.getHours() + (data.windowH ?? 0));

    const inboundAfter = data.inbound;
    const inboundBefore = data.windowH && data.inbound ? new Date(data.inbound) : undefined;
    inboundBefore?.setHours(inboundBefore.getHours() + (data.windowH ?? 0));

    return {
      origin: coordinatesParser.toSchema(data.origin),
      destination: coordinatesParser.toSchema(data.destination),
      departureAfter: outboundAfter.toISOString(),
      departureBefore: outboundBefore?.toISOString(),
      returnDepartureAfter: inboundAfter?.toISOString(),
      returnDepartureBefore: inboundBefore?.toISOString(),
    };
  },
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
