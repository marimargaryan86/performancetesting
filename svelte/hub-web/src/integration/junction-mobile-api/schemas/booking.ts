import type { CabinClass, CabinClassSchema } from "integration/common/schemas/cabin-class";
import type { IncludedMapping } from "./included";
import type { LegType, LegTypeSchema } from "integration/common/schemas/leg-type";
import type { Order, OrderSchema } from "./order";
import {
  offerSegmentLegParser,
  type OfferSegmentLeg,
  type OfferSegmentLegSchema,
} from "integration/common/schemas/offer-segment-leg";
import {
  routeIdentifiersParser,
  type RouteIdentifiers,
  type RouteIdentifiersSchema,
} from "integration/common/schemas/route-identifier";
import { priceParser, type PriceSchema, type Price } from "integration/common/schemas/price";
import type { BookingCancellation, BookingCancellationSchema } from "./cancellation";

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
  id: "confirmed" | "error" | "not-ticketed" | "cancelled" | "rejected";
  type: "booking-statuses";
};

export type TripBooking = {
  id: string;
  price: {
    total: Price;
  };
  ticketUrls: string[];
  operatorBookingReferences: string[];
  externalReference: string;
  status: BookingStatusSchema["id"];
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
    operatorBookingReferences: string[];
    externalReference: string;
    ticketUrls?: string[];
  };
  relationships: {
    order: { data: Pick<OrderSchema, "id" | "type"> };
    status: { data: Pick<BookingStatusSchema, "id" | "type"> };
    details?: { data?: Pick<TripBookingDetailsSchema, "id" | "type">[] };
    bookingCancellation: { data: Pick<BookingCancellationSchema, "id" | "type"> | null } | null;
  };
  links: { self: string };
};

export const tripBookingParser = {
  toModel: (data: TripBookingSchema, included?: IncludedMapping): TripBooking => {
    const orderId = data.relationships.order.data.id;
    const detailsIds = data.relationships.details?.data?.map(({ id }) => id) ?? [];
    const cancellationId = data.relationships.bookingCancellation?.data?.id;

    return {
      id: data.id,
      price: {
        total: priceParser.toModel(data.attributes.totalPrice),
      },
      ticketUrls: data.attributes.ticketUrls ?? [],
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
