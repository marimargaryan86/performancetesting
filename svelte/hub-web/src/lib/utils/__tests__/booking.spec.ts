import { describe, expect, it } from "vitest";
import type * as MobileSchemas from "~/integration/junction-mobile-api/schemas";
import type * as CommonSchemas from "~/integration/common/schemas";
import { validatePassengerNameRecord, getDestination } from "$lib/utils/booking";
import type { Point } from "~/integration/common/schemas";
import type { DeepPartial } from "~/integration/ts-helpers";

describe("validatePassengerNameRecord", () => {
  it("should return `true` for valid reference numbers", () => {
    expect(validatePassengerNameRecord("abc12345")).toBe(true);
    expect(validatePassengerNameRecord("abcdEFGH")).toBe(true);
    expect(validatePassengerNameRecord("12345678")).toBe(true);
  });

  it("should return `false` for invalid reference numbers", () => {
    // not 8 characters
    expect(validatePassengerNameRecord("abc12")).toBe(false);
    // more than 8 characters
    expect(validatePassengerNameRecord("abcdefghi")).toBe(false);
    // includes non-alphanumeric character
    expect(validatePassengerNameRecord("abcd-123")).toBe(false);
  });
});

describe("getDestination", () => {
  it("should return the destination of the last leg in the booking details", () => {
    // Helper function to create a point quickly
    const createPoint = (name: string): Point => ({
      ref: "ref",
      name,
      coordinates: { lat: 9.876, lon: 3.21 },
      timeZone: "UTC",
    });

    const leg1point = createPoint("leg1");
    const leg2point = createPoint("leg2");
    const leg3point = createPoint("leg3");

    const leg = (origin: Point, destination: Point): CommonSchemas.OfferSegmentLeg => ({
      origin,
      destination,
      departureAt: new Date(),
      arrivalAt: new Date(),
    });

    // Using the helper function to create legs compactly
    const booking: DeepPartial<MobileSchemas.TripBooking> = {
      detailsList: [
        {
          legs: [leg(leg1point, leg2point), leg(leg2point, leg3point), leg(leg3point, leg1point)],
        },
      ],
    };

    expect(getDestination(booking as MobileSchemas.TripBooking)).toEqual(leg1point);
  });

  it("should return undefined if the booking details or legs are empty", () => {
    const booking: DeepPartial<MobileSchemas.TripBooking> = {
      detailsList: [],
    };
    expect(getDestination(booking as MobileSchemas.TripBooking)).toBeUndefined();

    const bookingWithEmptyLegs: DeepPartial<MobileSchemas.TripBooking> = {
      detailsList: [
        {
          legs: [],
        },
      ],
    };
    expect(getDestination(bookingWithEmptyLegs as MobileSchemas.TripBooking)).toBeUndefined();
  });
});
