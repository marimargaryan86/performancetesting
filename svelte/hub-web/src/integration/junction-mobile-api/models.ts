import type { CoordinatesModel } from "models/booking/location";
import type { PassengerGender, PassengerTitle } from "./schemas/order";

export interface CreateTripCandidatesModel {
  sessionToken: string;
  criteria: {
    origin: CoordinatesModel;
    destination: CoordinatesModel;
    departureAfter: Date;
  }[];
  passengers: { dateOfBirth: Date }[];
  allowedLegTypeIds?: string[];
}

export interface CreateOrderModel {
  quoteId: string;
  paymentId: string;
  passengers: {
    firstName: string;
    lastName: string;
    title: PassengerTitle;
    gender: PassengerGender;
    dateOfBirth: Date;
    travelerDocument?:
      | { type: undefined }
      | {
          type: "passport";
          number?: string;
        };
  }[];
  contactDetails: {
    address: {
      addressLines: string[];
      city: string;
      countryCode: string;
      postalCode: string;
    };
    email: string;
    phone: {
      countryCode: string;
      number: string;
    };
  };
}
