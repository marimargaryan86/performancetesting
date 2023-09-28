import {
  bookingDetailsModel,
  offerSegmentLegModel,
  type BookingDetailsSchema,
  type BookingSchema,
  type BookingDetailsModel,
  bookingModel,
  type BookingModel,
  type BookingIncludes,
} from "../schemas/booking";
import type { JourneySchema } from "../schemas/journey";
import {
  legTypeModel,
  type CabinClassSchema,
  type LegTypeSchema,
  cabinClassModel,
} from "../schemas/offer";
import type { OrderSchema } from "../schemas/order";
import { parseOrder } from "./order";

export function parseBookingDetails(
  data: BookingDetailsSchema,
  included: {
    cabinClasses?: CabinClassSchema[];
    legTypes?: LegTypeSchema[];
  } = {},
): BookingDetailsModel {
  const parsed = bookingDetailsModel.toModel(data);
  const legType = included.legTypes?.find((item) => item.id === data.relationships.legType.data.id);
  const cabinClass = included.cabinClasses?.find(
    (item) => item.id === data.relationships.cabinClass.data.id,
  );

  return {
    ...parsed,
    legs: data.attributes.legs.map(offerSegmentLegModel.toModel),
    cabinClass: cabinClass ? cabinClassModel.toModel(cabinClass) : parsed.cabinClass,
    legType: legType ? legTypeModel.toModel(legType) : undefined,
  };
}

export function parseBooking(booking: BookingSchema, included: BookingIncludes[]): BookingModel {
  const order = included.find((item): item is OrderSchema => item.type === "orders");
  const details = included.find(
    (item): item is BookingDetailsSchema => item.type === "trip-booking-details",
  );
  const cabinClasses = included.filter(
    (item): item is CabinClassSchema => item.type === "cabin-classes",
  );
  const legTypes = included.filter((item): item is LegTypeSchema => item.type === "leg-types");
  const journeys = included.filter((item): item is JourneySchema => item.type === "journeys");

  return {
    ...bookingModel.toModel(booking),
    details: details ? parseBookingDetails(details, { cabinClasses, legTypes }) : undefined,
    order: order ? parseOrder(order, journeys) : undefined,
  };
}
