import type { CabinClass, CabinClassSchema } from "./cabin-class";
import type { BookingCancellation, BookingCancellationSchema } from "./cancellation";
import type { IncludedMapping } from "./included";
import type { LegType, LegTypeSchema } from "./leg-type";
import {
  priceParser,
  type Price,
  type PriceBreakdown,
  type PriceBreakdownSchema,
  type PriceSchema,
  priceBreakdownParser,
} from "./money";
import type { Order, OrderSchema } from "./order";
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

export type RouteIdentifiers = {
  vendor: string;
  operator?: string;
};

export type RouteIdentifiersSchema = {
  vendor: string;
  operator: string | null;
};

export const routeIdentifiersParser = {
  toModel: (data: RouteIdentifiersSchema): RouteIdentifiers => ({
    vendor: data.vendor,
    operator: data.operator ?? undefined,
  }),
};

export type TripBookingDetails = {
  id: string;
  cabinClassName: string;
  vendor: string;
  operator?: string;
  routeIdentifiers: RouteIdentifiers;
  legs: OfferSegmentLeg[];
  bookingId: string;
  booking?: TripBooking;
  cabinClassId: string;
  cabinClass?: CabinClass;
  legTypeId: string;
  legType?: LegType;
};

export type TripBookingDetailsSchema = {
  id: string;
  type: "trip-booking-details";
  attributes: {
    cabinClassName: string;
    vendor: string;
    operator: string | null;
    routeIdentifiers: RouteIdentifiersSchema;
    legs: OfferSegmentLegSchema[];
  };
  relationships: {
    booking: { data: Pick<TripBookingSchema, "id" | "type"> };
    cabinClass: { data: Pick<CabinClassSchema, "id" | "type"> };
    legType: { data: Pick<LegTypeSchema, "id" | "type"> };
  };
  links: { self: string };
};

export const tripBookingDetailsParser = {
  toModel: (data: TripBookingDetailsSchema, included?: IncludedMapping): TripBookingDetails => {
    const bookingId = data.relationships.booking.data.id;
    const cabinClassId = data.relationships.cabinClass.data.id;
    const legTypeId = data.relationships.legType.data.id;

    return {
      id: data.id,
      cabinClassName: data.attributes.cabinClassName,
      vendor: data.attributes.vendor,
      operator: data.attributes.operator ?? undefined,
      routeIdentifiers: routeIdentifiersParser.toModel(data.attributes.routeIdentifiers),
      legs: data.attributes.legs.map(offerSegmentLegParser.toModel),
      bookingId,
      booking: included?.tripBookings?.find(({ id }) => id === bookingId),
      cabinClassId,
      cabinClass: included?.cabinClasses?.find(({ id }) => id === cabinClassId),
      legTypeId,
      legType: included?.legTypes?.find(({ id }) => id === legTypeId),
    };
  },
};

export type BookingStatusSchema = {
  id: string;
  type: "booking-statuses";
};

export type TripBooking = {
  id: string;
  price: {
    total: Price;
    breakdown: PriceBreakdown[];
  };
  operatorBookingReferences: string[];
  externalReference: string;
  status: string;
  orderId: string;
  order?: Order;
  detailsIds: string[];
  detailsList: TripBookingDetails[];
  cancellationId?: string;
  cancellation?: BookingCancellation;
};

export type TripBookingSchema = {
  id: string;
  type: "trip-bookings";
  attributes: {
    totalPrice: PriceSchema;
    priceBreakdown?: PriceBreakdownSchema[];
    operatorBookingReferences: string[];
    externalReference: string;
  };
  relationships: {
    order: { data: Pick<OrderSchema, "id" | "type"> };
    status: { data: Pick<BookingStatusSchema, "id" | "type"> };
    details: { data: Pick<TripBookingDetailsSchema, "id" | "type">[] };
    bookingCancellation: { data: Pick<BookingCancellationSchema, "id" | "type"> | null };
  };
  links: { self: string };
};

export const tripBookingParser = {
  toModel: (data: TripBookingSchema, included?: IncludedMapping): TripBooking => {
    const orderId = data.relationships.order.data.id;
    const detailsIds = data.relationships.details.data.map(({ id }) => id);
    const cancellationId = data.relationships.bookingCancellation.data?.id ?? undefined;

    return {
      id: data.id,
      price: {
        total: priceParser.toModel(data.attributes.totalPrice),
        breakdown: data.attributes.priceBreakdown?.map(priceBreakdownParser.toModel) ?? [],
      },
      operatorBookingReferences: data.attributes.operatorBookingReferences,
      externalReference: data.attributes.externalReference,
      status: data.relationships.status.data.id,
      orderId,
      order: included?.orders?.find(({ id }) => id === orderId),
      detailsIds,
      detailsList: included?.tripBookingDetails?.filter(({ id }) => detailsIds.includes(id)) ?? [],
      cancellationId,
      cancellation: included?.bookingCancellations?.find(({ id }) => id === cancellationId),
    };
  },
};
