import {
  orderMarkupsModel,
  orderModel,
  type OrderMarkupsModel,
  type OrderMarkupsSchema,
  type OrderModel,
  type OrderSchema,
} from "../schemas/order";
import type { JourneyModel } from "../schemas/journey";
import type { BookingModel } from "../schemas/booking";

function getOrderStatus(bookings: BookingModel[]): OrderModel["status"] {
  const statuses = Array.from(new Set(bookings.flatMap((booking) => booking.status)));

  if (statuses.length === 1 && statuses[0]) {
    return statuses[0];
  }

  return "unknown";
}

export function parseOrderSchema(
  data: OrderSchema,
  included: {
    journeys?: JourneyModel[];
    bookings?: BookingModel[];
  } = {},
): OrderModel {
  const parsed = orderModel.toModel(data);
  const bookings = included.bookings?.filter((item) => parsed.bookingIds.includes(item.id)) ?? [];

  return {
    ...parsed,
    status: getOrderStatus(bookings),
    bookings,
    journey: included.journeys?.find((item) => item.id === data.relationships.journey.data.id),
  };
}

export function parseOrderMarkupsSchema(
  data: OrderMarkupsSchema,
  included: {
    order?: OrderModel;
  } = {},
): OrderMarkupsModel {
  const parsed = orderMarkupsModel.toModel(data);
  const orderId = included.order?.id ?? "";

  return {
    ...parsed,
    orderId,
  };
}
