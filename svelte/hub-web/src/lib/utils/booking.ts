import type * as HubSchemas from "~/integration/junction-hub-api/schemas";
import type * as MobileSchemas from "~/integration/junction-mobile-api/schemas";
import type * as CommonSchemas from "~/integration/common/schemas";

export function getOrigin(
  booking: MobileSchemas.TripBooking | HubSchemas.TripBooking,
): CommonSchemas.Point | undefined {
  return booking.detailsList[0]?.legs[0]?.origin;
}

export function getDestination(
  booking: MobileSchemas.TripBooking | HubSchemas.TripBooking,
): CommonSchemas.Point | undefined {
  const details = booking.detailsList[booking.detailsList.length - 1];

  return details?.legs[(details?.legs.length ?? 0) - 1]?.destination;
}

/**
 * Validates that the input `Journey.passengerNameRecord` is an 8 character length
 * alphanumeric string.
 *
 * @param passengerNameRecord A Journey passengerNameRecord to search
 * @returns Boolean indicating if a reference number is valid.
 */
export function validatePassengerNameRecord(passengerNameRecord: string | undefined): boolean {
  if (passengerNameRecord === undefined) {
    return false;
  }

  const regex = /^[A-Za-z0-9]{8}$/;

  return regex.test(passengerNameRecord);
}
