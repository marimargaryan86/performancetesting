import { error } from "@sveltejs/kit";
import integrationInstances from "integration-instances";
import type { TripBooking } from "integration/junction-mobile-api/schemas/booking";
import type { Order } from "integration/junction-mobile-api/schemas/order";
import { getSession } from "utils/auth";

export async function load(
  event,
): Promise<{ order: Order; booking: TripBooking; bookingNo: number }> {
  const order = await integrationInstances.junctionMobileApi.orders.getOrder({
    session: getSession(event),
    id: event.params.orderId,
  });
  const booking = order.bookings.find((item) => item.id === event.params.bookingId);

  if (!booking) {
    throw error(404, "Booking not found");
  }

  return { order, booking, bookingNo: order.bookings.indexOf(booking) + 1 };
}
