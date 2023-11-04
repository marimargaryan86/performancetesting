import type { TripBooking, TripBookingSchema } from "./booking";
import type { IncludedMapping } from "./included";

export type BookingCancellation = {
  id: string;
  status: string;
  bookingId: string;
  booking?: TripBooking;
};

export type BookingCancellationSchema = {
  id: string;
  type: "booking-cancellation";
  attributes: {
    status: "unspecified" | "pending" | "completed";
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

export type CancellationRequestCreate = {
  bookingIds: string[];
};

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
