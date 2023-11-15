import { error } from "@sveltejs/kit";
import integrationInstances from "integration-instances";
import type { TripBooking } from "integration/junction-hub-api/schemas/booking";

export async function load(event): Promise<{ booking: TripBooking; bookingNo: number }> {
  const booking = await integrationInstances.junctionHubApi.bookings.get({
    session: event.locals.session,
    id: event.params.bookingId,
  });

  if (!booking) {
    throw error(404, "Booking not found");
  }

  return {
    booking,
    bookingNo: (booking.order?.bookings.findIndex(({ id }) => id === booking.id) ?? 0) + 1,
  };
}
