import type * as CommonSchemas from "~/integration/common/schemas";
import type * as HubSchemas from "~/integration/junction-hub-api/schemas";

export function getOrderDepartureDate(order: HubSchemas.Order): { date: Date; timeZone: string } {
  const departureLeg = order.bookings
    .flatMap((booking) => booking.detailsList.flatMap((details) => details.legs))
    .sort((a, b) => {
      return a.departureAt.getTime() - b.departureAt.getTime();
    })[0];

  if (!departureLeg) {
    throw new Error("Unknown departure date");
  }

  return {
    date: departureLeg.departureAt,
    timeZone: departureLeg.origin.timeZone,
  };
}

export function getPassengerNames(order: HubSchemas.Order): string[] {
  return order.passengers.map((passenger) => `${passenger.firstName} ${passenger.lastName}`);
}

export function getTotalPrice(order: HubSchemas.Order): CommonSchemas.Price {
  const prices = order.bookings.flatMap((booking) => booking.price.total);

  return prices.reduce((prev, curr) => ({
    amount: prev.amount + curr.amount,
    currency: curr.currency,
  }));
}
