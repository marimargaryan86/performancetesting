import type { BookingCancellation, BookingCancellationSchema } from "./cancellation";
import type { IncludedMapping } from "./included";
import type { Order, OrderSchema } from "./order";
import * as CommonSchemas from "~/integration/common/schemas";
import type { Transaction, TransactionSchema } from "./transaction";
import type { Refund, RefundSchema } from "./refund";

export type OfferSegmentDetailRule = {
  title: string;
  body: string;
};

export type OfferSegmentDetailRuleSchema = {
  title: string;
  body: string;
};

export const offerSegmentDetailRuleParser = {
  toModel: (data: OfferSegmentDetailRuleSchema): OfferSegmentDetailRule => ({ ...data }),
};

export type TripBookingDetails = {
  id: string;
  cabinClassName: string;
  vendor: string;
  operator?: string;
  routeIdentifiers: CommonSchemas.RouteIdentifiers;
  legs: CommonSchemas.OfferSegmentLeg[];
  bookingId: string;
  booking?: TripBooking;
  cabinClassId: string;
  cabinClass?: CommonSchemas.CabinClass;
  legTypeId: string;
  legType?: CommonSchemas.LegType;
};

export type TripBookingDetailsSchema = {
  id: string;
  type: "trip-booking-details";
  attributes: {
    cabinClassName: string;
    vendor: string;
    operator: string | null;
    routeIdentifiers: CommonSchemas.RouteIdentifiersSchema;
    legs: CommonSchemas.OfferSegmentLegSchema[];
  };
  relationships: {
    booking: { data: Pick<TripBookingSchema, "id" | "type"> };
    cabinClass: { data: Pick<CommonSchemas.CabinClassSchema, "id" | "type"> };
    legType: { data: Pick<CommonSchemas.LegTypeSchema, "id" | "type"> };
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
      routeIdentifiers: CommonSchemas.routeIdentifiersParser.toModel(
        data.attributes.routeIdentifiers,
      ),
      legs: data.attributes.legs.map(CommonSchemas.offerSegmentLegParser.toModel),
      bookingId,
      booking: included?.tripBookings?.find(({ id }) => id === bookingId),
      cabinClassId,
      cabinClass: included?.cabinClasses?.find(({ id }) => id === cabinClassId),
      legTypeId,
      legType: included?.legTypes?.find(({ id }) => id === legTypeId),
    };
  },
};

export const bookingStatuses = [
  "cancelled",
  "confirmed",
  "error",
  "not-ticketed",
  "rejected",
] as const;

export type BookingStatus = (typeof bookingStatuses)[number];

export type BookingStatusSchema = {
  id: BookingStatus;
  type: "booking-statuses";
};

export type TripBooking = {
  id: string;
  price: {
    total: CommonSchemas.Price;
    breakdown: CommonSchemas.PriceBreakdown[];
  };
  operatorBookingReferences: string[];
  externalReference: string;
  rules: OfferSegmentDetailRule[];
  ticketUrls: string[];
  status: BookingStatusSchema["id"];
  orderId: string;
  order?: Order;
  detailsIds: string[];
  detailsList: TripBookingDetails[];
  cancellationId?: string;
  cancellation?: BookingCancellation;
  transactionId?: string;
  transaction?: Transaction;
  refundId?: string;
  refund?: Refund;
};

export type TripBookingSchema = {
  id: string;
  type: "trip-bookings";
  attributes: {
    totalPrice: CommonSchemas.PriceSchema;
    priceBreakdown?: CommonSchemas.PriceBreakdownSchema[];
    operatorBookingReferences: string[];
    externalReference: string;
    rules?: OfferSegmentDetailRuleSchema[];
    ticketUrls?: string[];
  };
  relationships: {
    order: { data: Pick<OrderSchema, "id" | "type"> };
    status: { data: Pick<BookingStatusSchema, "id" | "type"> };
    details: { data: Pick<TripBookingDetailsSchema, "id" | "type">[] };
    bookingCancellation: { data: Pick<BookingCancellationSchema, "id" | "type"> | null };
    transaction: { data: Pick<TransactionSchema, "id" | "type"> | null };
    refund: { data: Pick<RefundSchema, "id" | "type"> | null };
  };
  links: { self: string };
};

export const tripBookingParser = {
  toModel: (data: TripBookingSchema, included?: IncludedMapping): TripBooking => {
    const orderId = data.relationships.order.data.id;
    const detailsIds = data.relationships.details.data.map(({ id }) => id);
    const cancellationId = data.relationships.bookingCancellation.data?.id ?? undefined;
    const transactionId = data.relationships.transaction.data?.id ?? undefined;
    const refundId = data.relationships.refund.data?.id ?? undefined;

    return {
      id: data.id,
      price: {
        total: CommonSchemas.priceParser.toModel(data.attributes.totalPrice),
        breakdown:
          data.attributes.priceBreakdown
            ?.filter((pb) => pb.breakdownType !== "service-mark-up")
            ?.map(CommonSchemas.priceBreakdownParser.toModel) ?? [],
      },
      operatorBookingReferences: data.attributes.operatorBookingReferences,
      externalReference: data.attributes.externalReference,
      rules: data.attributes.rules?.map(offerSegmentDetailRuleParser.toModel) ?? [],
      ticketUrls: data.attributes.ticketUrls ?? [],
      status: data.relationships.status.data.id,
      orderId,
      order: included?.orders?.find(({ id }) => id === orderId),
      detailsIds,
      detailsList: included?.tripBookingDetails?.filter(({ id }) => detailsIds.includes(id)) ?? [],
      cancellationId,
      cancellation: included?.bookingCancellations?.find(({ id }) => id === cancellationId),
      transactionId,
      transaction: included?.transactions?.find(({ id }) => id === transactionId),
      refundId,
      refund: included?.refunds?.find(({ id }) => id === refundId),
    };
  },
};
