import type { RelationshipSchema } from "integration/common/schemas";
import type { PointSchema } from "./common";
import type { JourneySchema } from "./journey";
import type {
  CabinClassIdentifierSchema,
  CabinClassSchema,
  LegTypeIdentifierSchema,
  LegTypeSchema,
} from "./offer";
import type { OrderIdentifierSchema, OrderSchema } from "./order";
import type { PriceSchema } from "./price";

export interface BookingStatusIdentifierSchema {
  id: string;
  type: "booking-statuses";
}

export interface BookingDetailsIdentifierSchema {
  id: string;
  type: "trip-booking-details";
}

export interface BookingDetailsSchema extends BookingDetailsIdentifierSchema {
  attributes: {
    cabinClassName: string;
    vendor: string;
    operator: string | null;
    routeIdentifiers: {
      vendor: string;
      operator: string | null;
    };
    legs: {
      origin: PointSchema;
      destination: PointSchema;
      departureAt: string;
      arrivalAt: string;
    }[];
  };
  relationships: {
    booking: RelationshipSchema<BookingIdentifierSchema>;
    cabinClass: RelationshipSchema<CabinClassIdentifierSchema>;
    legType: RelationshipSchema<LegTypeIdentifierSchema>;
  };
  links: { self: string };
}

export interface BookingIdentifierSchema {
  id: string;
  type: "trip-bookings";
}

export interface BookingSchema extends BookingIdentifierSchema {
  attributes: {
    totalPrice: PriceSchema;
    operatorBookingReferences: string[];
    externalReference: string;
  };
  relationships: {
    order: RelationshipSchema<OrderIdentifierSchema>;
    status: RelationshipSchema<BookingStatusIdentifierSchema>;
    details: RelationshipSchema<BookingDetailsIdentifierSchema[]>;
  };
  links: { self: string };
}

export interface GetBookingResponseSchema {
  data: BookingSchema;
  included: (
    | OrderSchema
    | JourneySchema
    | BookingDetailsSchema
    | CabinClassSchema
    | LegTypeSchema
  )[];
}
