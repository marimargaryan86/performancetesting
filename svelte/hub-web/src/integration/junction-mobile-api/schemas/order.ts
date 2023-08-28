import type { RelationshipSchema } from "integration/common/schemas";
import type {
  CabinClassIdentifierSchema,
  CabinClassSchema,
  LegTypeIdentifierSchema,
  LegTypeSchema,
  OfferSegmentLegSchema,
  RouteIdentifiersSchema,
  TripOfferPriceQuoteIdentifierSchema,
} from "./offer";
import type { JourneyIdentifierSchema, JourneySchema } from "./journey";
import type { PriceSchema } from "./price";

export interface PaymentIdentifierSchema {
  id: string;
  type: "payments";
}

export interface VoucherIdentifierSchema {
  id: string;
  type: "vouchers";
}

export interface OrderIdentifierSchema {
  id: string;
  type: "orders";
}

export interface AddressSchema {
  addressLines: string[];
  countryCode: string;
  postalCode: string;
  city: string;
}

export interface ContactDetailsSchema {
  email: string;
  address: AddressSchema;
  phoneNumber: string;
}

export type PassengerTitle = "unspecified" | "mr" | "mrs" | "ms" | "miss";
export type PassengerGender = "unspecified" | "male" | "female";

export interface PassportDocumentSchema {
  documentType: "passport";
  documentNumber?: string;
  documentIssueCountry?: string;
  documentExpirationDate?: string;
  documentIssueDate?: string;
  nationality?: string;
  residenceCountryCode?: string;
}

export type TravelerDocumentSchema = { documentType: undefined } | PassportDocumentSchema;

export interface OrderPassengerSchema {
  firstName: string;
  lastName: string;
  title: PassengerTitle;
  gender: PassengerGender;
  dateOfBirth: string;
  travelerDocument?: TravelerDocumentSchema | null;
}

export interface BookingDetailsIdentifierSchema {
  id: string;
  type: "trip-booking-details";
}

export interface BookingDetailsSchema extends BookingDetailsIdentifierSchema {
  attributes: {
    cabinClassName: string;
    vendor: string;
    operator: string;
    routeIdentifiers: RouteIdentifiersSchema;
    legs: OfferSegmentLegSchema[];
  };
  relationships: {
    booking: RelationshipSchema<BookingIdentifierSchema>;
    cabinClass: RelationshipSchema<CabinClassIdentifierSchema>;
    legType: RelationshipSchema<LegTypeIdentifierSchema>;
  };
  links: { self: string };
}

export interface BookingStatusIdentifierSchema {
  id: string;
  type: "booking-statuses";
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

export interface OrderSchema {
  id: string;
  type: "orders";
  attributes: {
    passengers: OrderPassengerSchema[];
    residenceAddress?: AddressSchema;
  };
  relationships: {
    payment: RelationshipSchema<PaymentIdentifierSchema>;
    voucher?: RelationshipSchema<VoucherIdentifierSchema>;
    journey: RelationshipSchema<JourneyIdentifierSchema>;
    bookings: RelationshipSchema<BookingIdentifierSchema[]>;
  };
  links: { self: string };
}

export type CreateOrderSchema = Omit<
  OrderSchema,
  "id" | "relationships" | "attributes" | "links"
> & {
  attributes: OrderSchema["attributes"] & {
    contactDetails: ContactDetailsSchema;
  };
  relationships: Omit<OrderSchema["relationships"], "journey" | "bookings"> & {
    quote: RelationshipSchema<TripOfferPriceQuoteIdentifierSchema>;
  };
};

export interface CreateOrderRequestSchema {
  data: CreateOrderSchema;
}

export interface CreateOrderResponseSchema {
  data: OrderSchema;
}

export type OrderIncludesSchema = (
  | JourneySchema
  | BookingSchema
  | BookingDetailsSchema
  | CabinClassSchema
  | LegTypeSchema
)[];

export interface GetOrderResponseSchema {
  data: OrderSchema;
  included?: OrderIncludesSchema;
}

export interface ListOrdersResponseSchema {
  data: OrderSchema[];
  included?: OrderIncludesSchema;
  links: { next: string };
}
