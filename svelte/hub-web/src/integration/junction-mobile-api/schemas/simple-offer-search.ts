import * as CommonSchemas from "~/integration/common/schemas";
import type { TripCandidateSearch, TripCandidateSearchSchema } from "./trip-candidate";
import { tripOfferPassengerParser } from "./offer-search";

export type SimpleOfferSearchCriteria = {
  origin: CommonSchemas.Coordinates;
  destination: CommonSchemas.Coordinates;
  outbound: Date;
  inbound?: Date;
  windowH?: number;
};

export type SimpleOfferSearchCriteriaSchema = {
  origin: CommonSchemas.CoordinatesSchema;
  destination: CommonSchemas.CoordinatesSchema;
  departureAfter: string;
  departureBefore?: string | null;
  arrivalBefore?: string | null;
  returnDepartureBefore?: string | null;
  returnDepartureAfter?: string | null;
};

export const simpleOfferSearchCriteriaParser = {
  toModel: (
    data: SimpleOfferSearchCriteriaSchema,
    isCarSearch: boolean,
  ): SimpleOfferSearchCriteria => {
    const outboundAfter = new Date(data.departureAfter);
    const outboundBefore = data.departureBefore ? new Date(data.departureBefore) : undefined;
    const windowH = outboundBefore
      ? (outboundAfter.getTime() - outboundBefore.getTime()) / 3600000
      : undefined;
    let inbound = data.returnDepartureAfter ? new Date(data.returnDepartureAfter) : undefined;

    if (isCarSearch) {
      inbound = data.arrivalBefore ? new Date(data.arrivalBefore) : undefined;
    }

    return {
      origin: CommonSchemas.coordinatesParser.toModel(data.origin),
      destination: CommonSchemas.coordinatesParser.toModel(data.destination),
      outbound: new Date(data.departureAfter),
      inbound,
      windowH,
    };
  },
  toSchema: (
    data: SimpleOfferSearchCriteria,
    isCarSearch: boolean,
  ): SimpleOfferSearchCriteriaSchema => {
    if (isCarSearch) {
      return {
        origin: CommonSchemas.coordinatesParser.toSchema(data.origin),
        destination: CommonSchemas.coordinatesParser.toSchema(data.destination),
        departureAfter: data.outbound.toISOString(),
        arrivalBefore: data.inbound?.toISOString(),
      };
    }

    const outboundAfter = data.outbound;
    const outboundBefore = data.windowH ? new Date(data.outbound) : undefined;
    outboundBefore?.setHours(outboundBefore.getHours() + (data.windowH ?? 0));

    const inboundAfter = data.inbound;
    const inboundBefore = data.windowH && data.inbound ? new Date(data.inbound) : undefined;
    inboundBefore?.setHours(inboundBefore.getHours() + (data.windowH ?? 0));

    return {
      origin: CommonSchemas.coordinatesParser.toSchema(data.origin),
      destination: CommonSchemas.coordinatesParser.toSchema(data.destination),
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
  toModel: (data: SimpleOfferSearchSchema): SimpleOfferSearch => {
    const isCarSearch = Boolean(
      data.relationships?.allowedSegmentTypes?.data.find((item) => item.id === "car"),
    );

    return {
      id: data.id,
      status: data.attributes.status,
      expiresAt: new Date(data.attributes.expiresAt),
      passengers: data.attributes.passengers.map(tripOfferPassengerParser.toModel),
      allowedSegmentTypes: data.relationships?.allowedSegmentTypes?.data.map(({ id }) => id) ?? [],
      criteria: simpleOfferSearchCriteriaParser.toModel(data.attributes.criteria, isCarSearch),
    };
  },
  toCreateSchema: (data: SimpleOfferSearchCreate): SimpleOfferSearchCreateSchema => {
    const isCarSearch = Boolean(data.allowedSegmentTypes?.includes("car"));

    return {
      type: "simple-offer-searches",
      attributes: {
        sessionToken: data.sessionToken,
        criteria: simpleOfferSearchCriteriaParser.toSchema(data.criteria, isCarSearch),
        passengers: data.passengers.map(tripOfferPassengerParser.toSchema),
      },
      relationships: data.allowedSegmentTypes
        ? {
            allowedSegmentTypes: {
              data: data.allowedSegmentTypes.map((id) => ({ id, type: "leg-types" })),
            },
          }
        : undefined,
    };
  },
};
