import type { BookingDetailsModel, BookingModel } from "models/booking";
import type {
  BookingDetailsSchema,
  BookingSchema,
  GetBookingResponseSchema,
} from "../schemas/booking";
import type { JourneySchema } from "../schemas/journey";
import type { CabinClassSchema, LegTypeSchema } from "../schemas/offer";
import type { OrderSchema } from "../schemas/order";
import { parseOrder } from "./order";

export function parseBookingDetails(
  bookingDetails: BookingDetailsSchema,
  cabinClasses: CabinClassSchema[] = [],
  legTypes: LegTypeSchema[] = [],
): BookingDetailsModel {
  return {
    legs: bookingDetails.attributes.legs.map((item) => ({
      arrivalAt: new Date(item.arrivalAt),
      departureAt: new Date(item.departureAt),
      destination: item.destination,
      origin: item.origin,
    })),
    operator: bookingDetails.attributes.operator ?? undefined,
    routeIdentifiers: {
      vendor: bookingDetails.attributes.routeIdentifiers.vendor,
      operator: bookingDetails.attributes.routeIdentifiers.operator ?? undefined,
    },
    vendor: bookingDetails.attributes.vendor,
    cabinClass:
      cabinClasses?.find((item) => item.id === bookingDetails.relationships.cabinClass.data.id)
        ?.attributes.name ?? bookingDetails.attributes.cabinClassName,
    legType: legTypes.find((item) => item.id === bookingDetails.relationships.legType.data.id)
      ?.attributes.name,
  };
}

export function parseBooking(
  booking: BookingSchema,
  included: GetBookingResponseSchema["included"],
): BookingModel {
  const order = included.find((item): item is OrderSchema => item.type === "orders");
  const details = included.find(
    (item): item is BookingDetailsSchema => item.type === "trip-booking-details",
  );
  const cabinClasses = included.filter(
    (item): item is CabinClassSchema => item.type === "cabin-classes",
  );
  const legTypes = included.filter((item): item is LegTypeSchema => item.type === "leg-types");
  const journeys = included.filter((item): item is JourneySchema => item.type === "journeys");
  const { externalReference } = booking.attributes;

  return {
    id: booking.id,
    externalReference: externalReference.length ? externalReference : undefined,
    operatorReferences: booking.attributes.operatorBookingReferences,
    price: booking.attributes.totalPrice,
    status: booking.relationships.status.data.id,
    details: details ? parseBookingDetails(details, cabinClasses, legTypes) : undefined,
    order: order ? parseOrder(order, journeys) : undefined,
  };
}
