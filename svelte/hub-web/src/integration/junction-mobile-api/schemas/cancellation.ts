import type { TripBooking, TripBookingSchema } from "./booking";
import type { IncludedMapping } from "./included";

export type BookingCancellationStatus =
  | "unspecified"
  | "pending"
  | "completed"
  | "rejected"
  | "no-refund"
  | "refund-due"
  | "refund-issued";

export type BookingCancellation = {
  id: string;
  status: BookingCancellationStatus;
  bookingId: string;
  booking?: TripBooking;
};

export type BookingCancellationSchema = {
  id: string;
  type: "booking-cancellation";
  attributes: {
    status: BookingCancellationStatus;
  };
  relationships: {
    booking: { data: Pick<TripBookingSchema, "id" | "type"> };
  };
  links: { self: string };
};

export const bookingCancellationParser = {
  toModel: (data: BookingCancellationSchema, included?: IncludedMapping): BookingCancellation => {
    const bookingId = data.relationships.booking.data.id;

    return {
      id: data.id,
      status: data.attributes.status,
      bookingId,
      booking: included?.tripBookings?.find(({ id }) => id === bookingId),
    };
  },
};

export type CancellationRequest = {
  id: string;
  status: "unspecified" | "pending" | "completed";
  bookingIds: string[];
  bookings: TripBooking[];
};

export type CancellationRequestCreate = Pick<CancellationRequest, "bookingIds">;

export type CancellationRequestSchema = {
  id: string;
  type: "cancellation-request";
  attributes: {
    status: "unspecified" | "pending" | "completed";
  };
  relationships: {
    bookings: { data: Pick<TripBookingSchema, "id" | "type">[] };
  };
  links: { self: string };
};

export type CantellationRequestCreateSchema = Pick<
  CancellationRequestSchema,
  "type" | "relationships"
>;

export const cancellationRequestParsers = {
  toModel: (data: CancellationRequestSchema, included?: IncludedMapping): CancellationRequest => {
    const bookingIds = data.relationships.bookings.data.map(({ id }) => id);

    return {
      id: data.id,
      status: data.attributes.status,
      bookingIds,
      bookings: included?.tripBookings?.filter(({ id }) => bookingIds.includes(id)) ?? [],
    };
  },
  toCreateSchema: (data: CancellationRequestCreate): CantellationRequestCreateSchema => ({
    type: "cancellation-request",
    relationships: {
      bookings: { data: data.bookingIds.map((id) => ({ id, type: "trip-bookings" })) },
    },
  }),
};
