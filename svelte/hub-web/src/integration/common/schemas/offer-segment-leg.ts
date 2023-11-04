import { pointParser, type Point, type PointSchema } from "./point";

export type OfferSegmentLeg = {
  origin: Point;
  destination: Point;
  departureAt: Date;
  arrivalAt: Date;
};

export type OfferSegmentLegSchema = {
  origin: PointSchema;
  destination: PointSchema;
  departureAt: string;
  arrivalAt: string;
};

export const offerSegmentLegParser = {
  toModel: (data: OfferSegmentLegSchema): OfferSegmentLeg => ({
    origin: pointParser.toModel(data.origin),
    destination: pointParser.toModel(data.destination),
    arrivalAt: new Date(data.arrivalAt),
    departureAt: new Date(data.departureAt),
  }),
};
