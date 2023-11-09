import type { Order as MobileOrder } from "integration/junction-mobile-api/schemas/order";
import type { Order as HubOrder } from "integration/junction-hub-api/schemas/order";
import type { TripBooking as MobileTripBooking } from "integration/junction-mobile-api/schemas/booking";
import type { TripBooking as HubTripBooking } from "integration/junction-hub-api/schemas/booking";
import { ensureDefined } from "utils/array";

type Order = MobileOrder | HubOrder;
type TripBooking = MobileTripBooking | HubTripBooking;

export type OrderBookingStatus = TripBooking["status"] | "mixed";
export type OrderCancellationStatus = NonNullable<TripBooking["cancellation"]>["status"] | "mixed";
export type OrderRefundStatus = NonNullable<HubTripBooking["refund"]>["status"] | "mixed";

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
