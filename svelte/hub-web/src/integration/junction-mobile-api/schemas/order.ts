import type { TripBooking } from "./booking";
import type { Specification } from "./__generated__";
import type { IncludedMapping } from "./included";
import { contactDetailsParser, type ContactDetails, type Journey } from "./journey";
import type { Payment, Voucher } from "./payment";
import * as CommonSchemas from "~/integration/common/schemas";
import type { GetOKResponse, PostRequest } from "~/integration/common/types";

export type TravelerDocument = {
  type?: CommonSchemas.TravelerDocumentType;
  number?: string;
  expiryDate?: Date;
  issueDate?: Date;
  countryCodes?: {
    issue?: string;
    nationality?: string;
    residence?: string;
  };
};

export type TravelerDocumentSchema = NonNullable<OrderPassengerSchema["travelerDocument"]>;

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
  title: CommonSchemas.PassengerTitle;
  gender: CommonSchemas.Gender;
  birthDate: Date;
  document?: TravelerDocument;
};

export type OrderPassengerSchema = OrderSchema["attributes"]["passengers"][number];

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
  residenceAddress?: Required<Omit<CommonSchemas.EnhancedAddressDetails, "state">>;
  paymentId: string;
  payment?: Payment;
  voucherId?: string;
  voucher?: Voucher;
  journeyId: string;
  journey?: Journey;
  bookingIds: string[];
  bookings: TripBooking[];
};

export type OrderSchema = GetOKResponse<Specification, "/orders">["data"][number];

export type OrderCreate = Pick<
  Order,
  "passengers" | "residenceAddress" | "paymentId" | "voucherId"
> & {
  contact: ContactDetails;
  priceQuoteId: string;
};

export type OrderCreateSchema = PostRequest<Specification, "/orders">["data"];

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
        ? (CommonSchemas.enhancedAddressDetailsParser.toModel(
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
        ? (CommonSchemas.enhancedAddressDetailsParser.toSchema(
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
