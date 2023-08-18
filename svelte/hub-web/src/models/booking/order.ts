import type {
  PassengerGender,
  PassengerTitle,
} from "integration/junction-mobile-api/schemas/order";

export interface PassportDocumentModel {
  type: "passport";
  number?: string;
}

export type TravelerDocumentModel = { type: undefined } | PassportDocumentModel;

export interface OrderPassengerModel {
  firstName: string;
  lastName: string;
  title: PassengerTitle;
  gender: PassengerGender;
  dateOfBirth: Date;
  document?: TravelerDocumentModel;
}

export interface OrderModel {
  id: string;
  passengers: OrderPassengerModel[];
  paymentId: string;
  journeyId: string;
  bookingIds: string[];
}
