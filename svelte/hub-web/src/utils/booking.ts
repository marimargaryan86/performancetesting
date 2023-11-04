import type { TripBooking as MobileBooking } from "integration/junction-mobile-api/schemas/booking";
import type { TripBooking as HubBooking } from "integration/junction-hub-api/schemas/booking";
import type { Point } from "integration/common/schemas/point";

export function getOrigin(booking: MobileBooking | HubBooking): Point | undefined {
  return booking.detailsList[0]?.legs[0]?.origin;
}

export function getDestination(booking: MobileBooking | HubBooking): Point | undefined {
  const details = booking.detailsList[booking.detailsList.length - 1];

  return details?.legs[(details?.legs.length ?? 0) - 1]?.destination;
}
