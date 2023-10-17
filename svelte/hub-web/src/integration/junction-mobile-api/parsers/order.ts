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
import { ensureDefined } from "utils/array";

function getOrderStatus(bookings: BookingModel[]): OrderModel["status"] {
  const statuses = Array.from(new Set(bookings.map((booking) => booking.status)));

  if (statuses.length === 1 && statuses[0]) {
    return statuses[0];
  }

  return "unknown";
}

function getOrderCancellationStatus(bookings: BookingModel[]): OrderModel["cancellationStatus"] {
  const statuses = Array.from(
    bookings.map((booking) => booking.cancellationStatus).filter(ensureDefined),
  );

  if (statuses.length === bookings.length) {
    return "pending";
  }

  if (statuses.length) {
    return "unknown";
  }

  return undefined;
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
    get cancellationStatus(): OrderModel["cancellationStatus"] {
      return getOrderCancellationStatus(this.bookings);
    },
    get status(): OrderModel["status"] {
      return getOrderStatus(this.bookings);
    },
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
