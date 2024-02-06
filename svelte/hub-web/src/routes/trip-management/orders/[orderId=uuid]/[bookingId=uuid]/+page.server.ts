import { error } from "@sveltejs/kit";
import integrationInstances from "~/integration-instances";
import type { TripBooking } from "~/integration/junction-hub-api/schemas/booking";
import type { Markups } from "~/integration/junction-mobile-api/schemas/markups";

export async function load(
  event,
): Promise<{ booking: TripBooking; markups?: Markups; bookingNo: number }> {
  const [booking, markups] = await Promise.all([
    integrationInstances.junctionHubApi.bookings
      .get({
        session: event.locals.session,
        id: event.params.bookingId,
      })
      .catch(() => undefined),
    integrationInstances.junctionMobileApi.orders
      .getMarkups({
        session: event.locals.session,
        orderId: event.params.orderId,
      })
      .catch(() => undefined),
  ]);

  if (!booking) {
    throw error(404, "Booking not found");
  }

  return {
    booking,
    markups,
    bookingNo: (booking.order?.bookings.findIndex(({ id }) => id === booking.id) ?? 0) + 1,
  };
}
