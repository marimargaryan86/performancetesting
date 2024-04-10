import type { GetOKResponse } from "~/integration/common/types";
import type { TripBooking } from "./booking";
import type { IncludedMapping } from "./included";
import type { Journey } from "./journey";
import * as CommonSchemas from "~/integration/common/schemas";
import type { Specification } from "./__generated__";

export type TravelerDocument = {
  type?: CommonSchemas.TravelerDocumentType;
  number?: string;
  expiryDate?: Date;
  issueDate?: Date;
  countryCodes: {
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
    countryCodes: {
      issue: data.documentIssueCountry,
      nationality: data.nationality,
      residence: data.residenceCountryCode,
    },
  }),
};

export type OrderPassenger = {
  firstName: string;
  lastName: string;
  title: CommonSchemas.PassengerTitle;
  gender: CommonSchemas.Gender;
  birthDate: Date;
  travelerDocument?: TravelerDocument;
};

export type OrderPassengerSchema = OrderSchema["attributes"]["passengers"][number];

export const orderPassengerParser = {
  toModel: (data: OrderPassengerSchema): OrderPassenger => ({
    firstName: data.firstName,
    lastName: data.lastName,
    title: data.title,
    gender: data.gender,
    birthDate: new Date(data.dateOfBirth),
    travelerDocument: data.travelerDocument
      ? travelerDocumentParser.toModel(data.travelerDocument)
      : undefined,
  }),
};

export type Order = {
  id: string;
  createdAt: Date;
  passengers: OrderPassenger[];
  residenceAddress?: Required<Omit<CommonSchemas.EnhancedAddressDetails, "state">>;
  journeyId: string;
  journey?: Journey;
  bookingIds: string[];
  bookings: TripBooking[];
};

export type OrderSchema = GetOKResponse<Specification, "/orders/{orderId}">["data"];

export const orderParser = {
  toModel: (data: OrderSchema, included?: IncludedMapping): Order => {
    const journeyId = data.relationships.journey.data.id;
    const bookingIds = data.relationships.bookings.data.map(({ id }) => id);

    return {
      id: data.id,
      createdAt: new Date(data.attributes.createdAt),
      passengers: data.attributes.passengers.map(orderPassengerParser.toModel),
      residenceAddress: data.attributes.residenceAddress
        ? (CommonSchemas.enhancedAddressDetailsParser.toModel(
            data.attributes.residenceAddress,
          ) as Order["residenceAddress"])
        : undefined,
      journeyId,
      journey: included?.journeys?.find(({ id }) => id === journeyId),
      bookingIds,
      bookings: included?.tripBookings?.filter(({ id }) => bookingIds.includes(id)) ?? [],
    };
  },
};
