import type { BookingCancellation } from "./cancellation";
import type { IncludedMapping } from "./included";
import type { Order } from "./order";
import * as CommonSchemas from "~/integration/common/schemas";
import type { Transaction } from "./transaction";
import type { Refund } from "./refund";
import type { GetIncluded, GetOKResponse } from "~/integration/common/types";
import type { Specification } from "./__generated__";

export type OfferSegmentDetailRule = {
  title: string;
  body: string;
};

export type OfferSegmentDetailRuleSchema = NonNullable<
  TripBookingSchema["attributes"]["rules"]
>[number];

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

export type TripBookingDetailsSchema = GetIncluded<
  GetOKResponse<Specification, "/journeys">,
  "trip-booking-details"
>;

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

export type TripBookingSchema = GetIncluded<
  GetOKResponse<Specification, "/journeys">,
  "trip-bookings"
>;

export const tripBookingParser = {
  toModel: (data: TripBookingSchema, included?: IncludedMapping): TripBooking => {
    const orderId = data.relationships.order.data.id;
    const detailsIds = data.relationships.details.data.map(({ id }) => id);
    const cancellationId = data.relationships.bookingCancellation?.data?.id ?? undefined;
    const transactionId = data.relationships.transaction?.data?.id ?? undefined;
    const refundId = data.relationships.refund?.data?.id ?? undefined;

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
      status: data.relationships.status.data.id as BookingStatusSchema["id"],
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
