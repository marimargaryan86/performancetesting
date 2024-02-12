import type * as HubSchemas from "~/integration/junction-hub-api/schemas";
import type * as MobileSchemas from "~/integration/junction-mobile-api/schemas";
import { ensureDefined } from "$lib/utils/array";

type Order = MobileSchemas.Order | HubSchemas.Order;
type TripBooking = MobileSchemas.TripBooking | HubSchemas.TripBooking;

export type OrderBookingStatus = TripBooking["status"] | "mixed";
export type OrderCancellationStatus = NonNullable<TripBooking["cancellation"]>["status"] | "mixed";
export type OrderRefundStatus = NonNullable<HubSchemas.TripBooking["refund"]>["status"] | "mixed";

export type TravelerDocumentType = "passport";
export type Gender = "unspecified" | "male" | "female";
export type PassengerTitle = "unspecified" | "mr" | "mrs" | "ms" | "miss";

export const getOrderStatus = {
  booking(order: Order): OrderBookingStatus | undefined {
    const statuses = Array.from(new Set(order.bookings.flatMap((booking) => booking.status)));

    if (!statuses.length) {
      return undefined;
    }

    if (statuses.length === 1) {
      return statuses[0];
    }

    return "mixed";
  },
  cancellation(order: Order): OrderCancellationStatus | undefined {
    const statuses = Array.from(
      new Set(order.bookings.flatMap((booking) => booking.cancellation?.status)),
    ).filter(ensureDefined);

    if (!statuses.length) {
      return undefined;
    }

    if (statuses.length === 1) {
      return statuses[0];
    }

    return "mixed";
  },
  refund(order: Order): OrderRefundStatus | undefined {
    const statuses = Array.from(
      new Set(
        order.bookings.flatMap((booking) => {
          if ("refund" in booking) {
            return booking.refund?.status;
          }

          return undefined;
        }),
      ),
    );

    if (!statuses.length) {
      return undefined;
    }

    if (statuses.length === 1) {
      return statuses[0];
    }

    return "mixed";
  },
};
