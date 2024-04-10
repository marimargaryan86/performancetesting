import type { GetOKResponse, PostRequest } from "~/integration/common/types";
import type { TripBooking } from "./booking";
import type { IncludedMapping } from "./included";
import type { Specification } from "./__generated__";

export type BookingCancellationStatus = BookingCancellationSchema["attributes"]["status"];

export type BookingCancellation = {
  id: string;
  status: BookingCancellationStatus;
  bookingId: string;
  booking?: TripBooking;
};

export type BookingCancellationSchema = GetOKResponse<
  Specification,
  "/bookings/{bookingId}/cancellation"
>["data"];

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

export type CancellationRequestSchema = GetOKResponse<
  Specification,
  "/cancellations/requests/{cancellationRequestId}"
>["data"];

export type CancellationRequestCreateSchema = PostRequest<
  Specification,
  "/cancellations/requests"
>["data"];

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
  toCreateSchema: (data: CancellationRequestCreate): CancellationRequestCreateSchema => ({
    type: "cancellation-request",
    relationships: {
      bookings: { data: data.bookingIds.map((id) => ({ id, type: "trip-bookings" })) },
    },
  }),
};
