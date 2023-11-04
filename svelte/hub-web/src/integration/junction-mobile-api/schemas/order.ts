import {
  enhancedAddressDetailsParser,
  type EnhancedAddressDetails,
  type EnhancedAddressDetailsSchema,
} from "integration/common/schemas/address";
import type { BookingStatusSchema, TripBooking, TripBookingSchema } from "./booking";
import type { IncludedMapping } from "./included";
import {
  contactDetailsParser,
  type ContactDetails,
  type ContactDetailsSchema,
  type Journey,
  type JourneySchema,
} from "./journey";
import type { Payment, PaymentSchema, Voucher, VoucherSchema } from "./payment";
import type { TripOfferPriceQuoteSchema } from "./trip-offer-price-quote";
import type { BookingCancellationStatus } from "./cancellation";
import { ensureDefined } from "utils/array";

export type OrderStatus = BookingStatusSchema["id"] | "mixed" | "unknown";
export type OrderCancellationStatus = BookingCancellationStatus | "mixed" | undefined;

export const getOrderStatus = {
  cancellationStatus: (order: {
    bookings: {
      cancellation?: {
        status: NonNullable<Order["bookings"][number]["cancellation"]>["status"];
      };
    }[];
  }): OrderCancellationStatus => {
    const statuses = Array.from(
      new Set(order.bookings.map((item) => item.cancellation?.status).filter(ensureDefined)),
    );

    if (!statuses.length) {
      return undefined;
    }

    if (statuses.length === 1) {
      return statuses[0];
    }

    return "mixed";
  },
  status: (order: {
    bookings: {
      status: BookingStatusSchema["id"];
    }[];
  }): OrderStatus => {
    const statuses = Array.from(
      new Set(order.bookings.map((item) => item.status).filter(ensureDefined)),
    );

    if (!statuses.length) {
      return "unknown";
    }

    if (statuses.length === 1) {
      return statuses[0] as OrderStatus;
    }

    return "mixed";
  },
};

export type TravelerDocument = {
  type?: "passport";
  number?: string;
  expiryDate?: Date;
  issueDate?: Date;
  countryCodes?: {
    issue?: string;
    nationality?: string;
    residence?: string;
  };
};

export type TravelerDocumentSchema = {
  documentType?: "passport";
  documentNumber?: string;
  documentIssueCountry?: string;
  documentExpirationDate?: string;
  documentIssueDate?: string;
  nationality?: string;
  residenceCountryCode?: string;
};

export const travelerDocumentParser = {
  toModel: (data: TravelerDocumentSchema): TravelerDocument => ({
    type: data.documentType,
    number: data.documentNumber,
    expiryDate: data.documentExpirationDate ? new Date(data.documentExpirationDate) : undefined,
    issueDate: data.documentIssueDate ? new Date(data.documentIssueDate) : undefined,
    countryCodes:
      data.documentIssueCountry || data.nationality || data.residenceCountryCode
        ? {
            issue: data.documentIssueCountry,
            nationality: data.nationality,
            residence: data.residenceCountryCode,
          }
        : undefined,
  }),
  toSchema: (data: TravelerDocument): TravelerDocumentSchema => ({
    documentType: data.type,
    documentNumber: data.number,
    documentExpirationDate: data.expiryDate?.toLocaleDateString("sv-SE"),
    documentIssueCountry: data.countryCodes?.issue,
    documentIssueDate: data.issueDate?.toLocaleDateString("sv-SE"),
    nationality: data.countryCodes?.nationality,
    residenceCountryCode: data.countryCodes?.residence,
  }),
};

export type OrderPassenger = {
  firstName: string;
  lastName: string;
  title: "unspecified" | "mr" | "mrs" | "ms" | "miss";
  gender: "unspecified" | "male" | "female";
  birthDate: Date;
  document?: TravelerDocument;
};

export type OrderPassengerSchema = {
  firstName: string;
  lastName: string;
  title: "unspecified" | "mr" | "mrs" | "ms" | "miss";
  gender: "unspecified" | "male" | "female";
  dateOfBirth: string;
  travelerDocument?: TravelerDocumentSchema | null;
};

export const orderPassengerParser = {
  toModel: (data: OrderPassengerSchema): OrderPassenger => ({
    firstName: data.firstName,
    lastName: data.lastName,
    title: data.title,
    gender: data.gender,
    birthDate: new Date(data.dateOfBirth),
    document: data.travelerDocument
      ? travelerDocumentParser.toModel(data.travelerDocument)
      : undefined,
  }),
  toSchema: (data: OrderPassenger): OrderPassengerSchema => ({
    dateOfBirth: data.birthDate.toLocaleDateString("sv-SE"),
    firstName: data.firstName,
    gender: data.gender,
    lastName: data.lastName,
    title: data.title,
    travelerDocument: data.document ? travelerDocumentParser.toSchema(data.document) : undefined,
  }),
};

export type Order = {
  id: string;
  passengers: OrderPassenger[];
  residenceAddress?: Required<Omit<EnhancedAddressDetails, "state">>;
  paymentId: string;
  payment?: Payment;
  voucherId?: string;
  voucher?: Voucher;
  journeyId: string;
  journey?: Journey;
  bookingIds: string[];
  bookings: TripBooking[];
};

export type OrderSchema = {
  id: string;
  type: "orders";
  attributes: {
    passengers: OrderPassengerSchema[];
    residenceAddress?: Required<Omit<EnhancedAddressDetailsSchema, "state">>;
  };
  relationships: {
    payment: { data: Pick<PaymentSchema, "id" | "type"> };
    voucher?: { data: Pick<VoucherSchema, "id" | "type"> };
    journey: { data: Pick<JourneySchema, "id" | "type"> };
    bookings: { data: Pick<TripBookingSchema, "id" | "type">[] };
  };
  links: { self: string };
};

export type OrderCreate = Pick<
  Order,
  "passengers" | "residenceAddress" | "paymentId" | "voucherId"
> & {
  contact: ContactDetails;
  priceQuoteId: string;
};

export type OrderCreateSchema = Pick<OrderSchema, "type" | "attributes"> & {
  attributes: {
    contactDetails: ContactDetailsSchema;
  };
  relationships: Pick<OrderSchema["relationships"], "payment" | "voucher"> & {
    quote: { data: Pick<TripOfferPriceQuoteSchema, "id" | "type"> };
  };
};

export const orderParser = {
  toModel: (data: OrderSchema, included?: IncludedMapping): Order => {
    const journeyId = data.relationships.journey.data.id;
    const bookingIds = data.relationships.bookings.data.map(({ id }) => id);
    const paymentId = data.relationships.payment.data.id;
    const voucherId = data.relationships.voucher?.data.id;

    return {
      id: data.id,
      passengers: data.attributes.passengers.map(orderPassengerParser.toModel),
      residenceAddress: data.attributes.residenceAddress
        ? (enhancedAddressDetailsParser.toModel(
            data.attributes.residenceAddress,
          ) as Order["residenceAddress"])
        : undefined,
      paymentId,
      payment: included?.payments?.find(({ id }) => id === paymentId),
      voucherId,
      voucher: included?.vouchers?.find(({ id }) => id === voucherId),
      journeyId,
      journey: included?.journeys?.find(({ id }) => id === journeyId),
      bookingIds,
      bookings: included?.tripBookings?.filter(({ id }) => bookingIds.includes(id)) ?? [],
    };
  },
  toCreateSchema: (data: OrderCreate): OrderCreateSchema => ({
    type: "orders",
    attributes: {
      contactDetails: contactDetailsParser.toSchema(data.contact),
      passengers: data.passengers.map(orderPassengerParser.toSchema),
      residenceAddress: data.residenceAddress
        ? (enhancedAddressDetailsParser.toSchema(
            data.residenceAddress,
          ) as OrderSchema["attributes"]["residenceAddress"])
        : undefined,
    },
    relationships: {
      payment: { data: { id: data.paymentId, type: "payments" } },
      quote: { data: { id: data.priceQuoteId, type: "trip-offer-price-quotes" } },
      voucher: data.voucherId ? { data: { id: data.voucherId, type: "vouchers" } } : undefined,
    },
  }),
};
