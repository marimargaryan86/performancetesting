import type { BookingModel } from "integration/junction-mobile-api/schemas/booking";
import type { PointModel } from "integration/junction-mobile-api/schemas/common";
import { ensureDefined } from "./array";

export function getOrigin(booking: BookingModel): PointModel | undefined {
  return booking.details[0]?.legs[0]?.origin;
}

export function getDestination(booking: BookingModel): PointModel | undefined {
  const details = booking.details[booking.details.length - 1];

  return details?.legs[(details?.legs.length ?? 0) - 1]?.destination;
}

export function downloadTickets(bookings: BookingModel[]): void {
  if (typeof window === "undefined") {
    return;
  }

  const ticketUrls = bookings.map((item) => item.ticketUrl).filter(ensureDefined);

  ticketUrls.forEach((url) => window.open(url));
}
