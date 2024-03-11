import { describe, expect, it } from "vitest";
import { getOrderDepartureDate, getPassengerNames, getTotalPrice } from "$lib/utils/order";
import type { Order } from "~/integration/junction-hub-api/schemas";
import type { Price } from "~/integration/common/schemas";
import type { DeepPartial } from "~/integration/ts-helpers";

describe("order utils", () => {
  const mockLeg1 = {
    departureAt: new Date("2022-01-01T10:00:00Z"),
    origin: {
      timeZone: "America/New_York",
    },
  };

  const mockLeg2 = {
    departureAt: new Date("2022-01-01T05:00:00Z"),
    origin: {
      timeZone: "America/Los_Angeles",
    },
  };

  const mockBooking = {
    detailsList: [
      {
        legs: [mockLeg1],
      },
    ],
    price: {
      total: {
        amount: 100,
        currency: "USD",
      },
    },
  };

  const mockOrder = {
    bookings: [mockBooking],
    passengers: [
      {
        firstName: "John",
        lastName: "Doe",
      },
      {
        firstName: "Jane",
        lastName: "Doe",
      },
    ],
  } as DeepPartial<Order> as Order;

  describe("getOrderDepartureDate", () => {
    it("should return the departure date of an order with one leg", () => {
      const result = getOrderDepartureDate(mockOrder as Order);
      expect(result).toEqual({
        date: new Date("2022-01-01T10:00:00Z"),
        timeZone: "America/New_York",
      });
    });

    it("should return the departure date of an order with multiple legs", () => {
      const mockOrderWithMultipleLegs = {
        ...mockOrder,
        bookings: [
          {
            ...mockBooking,
            detailsList: [
              {
                legs: [mockLeg1, mockLeg2],
              },
            ],
          },
        ],
      };
      const result = getOrderDepartureDate(mockOrderWithMultipleLegs as Order);
      expect(result).toEqual({
        date: new Date("2022-01-01T05:00:00Z"),
        timeZone: "America/Los_Angeles",
      });
    });

    it("should throw an error when there are no legs", () => {
      const order = {
        ...mockOrder,
        bookings: [
          {
            detailsList: [
              {
                legs: [],
              },
            ],
          },
        ],
      } as DeepPartial<Order> as Order;

      expect(() => getOrderDepartureDate(order)).toThrow("Unknown departure date");
    });
  });

  describe("getPassengerNames", () => {
    it("should return the names of the passengers in the order", () => {
      const result = getPassengerNames(mockOrder as Order);
      expect(result).toEqual(["John Doe", "Jane Doe"]);
    });
  });

  describe("getTotalPrice", () => {
    it("should return the total price of an order with one booking", () => {
      const result = getTotalPrice(mockOrder as Order);
      expect(result).toEqual({
        amount: 100,
        currency: "USD",
      } as Price);
    });

    it("should return the total price of an order with multiple bookings", () => {
      const mockOrderWithMultipleBookings = {
        ...mockOrder,
        bookings: [mockBooking, mockBooking, mockBooking],
      };
      const result = getTotalPrice(mockOrderWithMultipleBookings as Order);
      expect(result).toEqual({
        amount: 300,
        currency: "USD",
      } as Price);
    });
  });
});
