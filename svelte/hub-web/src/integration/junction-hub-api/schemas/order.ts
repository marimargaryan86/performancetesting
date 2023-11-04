import {
  enhancedAddressDetailsParser,
  type EnhancedAddressDetails,
  type EnhancedAddressDetailsSchema,
} from "./address";
import type { TripBooking, TripBookingSchema } from "./booking";
import type { IncludedMapping } from "./included";
import type { Journey, JourneySchema } from "./journey";

export type TravelerDocument = {
  type?: "passport";
  number?: string;
  expiryDate?: Date;
  issueDate?: Date;
  countryCodes: {
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
  title: "unspecified" | "mr" | "mrs" | "ms" | "miss";
  gender: "unspecified" | "male" | "female";
  birthDate: Date;
  travelerDocument?: TravelerDocument;
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
    travelerDocument: data.travelerDocument
      ? travelerDocumentParser.toModel(data.travelerDocument)
      : undefined,
  }),
};

export type Order = {
  id: string;
  passengers: OrderPassenger[];
  residenceAddress?: Required<Omit<EnhancedAddressDetails, "state">>;
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
    journey: { data: Pick<JourneySchema, "id" | "type"> };
    bookings: { data: Pick<TripBookingSchema, "id" | "type">[] };
  };
  links: { self: string };
};

export const orderParser = {
  toModel: (data: OrderSchema, included?: IncludedMapping): Order => {
    const journeyId = data.relationships.journey.data.id;
    const bookingIds = data.relationships.bookings.data.map(({ id }) => id);

    return {
      id: data.id,
      passengers: data.attributes.passengers.map(orderPassengerParser.toModel),
      residenceAddress: data.attributes.residenceAddress
        ? (enhancedAddressDetailsParser.toModel(
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
