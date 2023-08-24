import type {
  PassengerGender,
  PassengerTitle,
} from "integration/junction-mobile-api/schemas/order";
import type { CabinClassModel, LegTypeModel, OfferSegmentLegModel } from "./offer";
import type { PriceModel } from "./money";

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
  journey?: JourneyModel;
  bookingIds: string[];
  bookings: BookingModel[];
}

export interface BookingModel {
  id: string;
  price: PriceModel;
  operatorBookingReferences: string[];
  externalReference: string;
  order?: OrderModel;
  status: string;
  details: BookingDetailsModel[];
}

export interface BookingDetailsModel {
  id: string;
  cabinClassName: string;
  vendor: string;
  operator: string;
  routeIdentifiers: {
    vendor: string;
    operator?: string;
  };
  legs: OfferSegmentLegModel[];
  bookingId: string;
  booking?: BookingModel;
  cabinClass?: CabinClassModel;
  legType?: LegTypeModel;
}

export interface JourneyModel {
  id: string;
  reference: string;
  contact: {
    email: string;
    phoneNumber: string;
    address: {
      addressLines: string[];
      countryCode: string;
      postalCode: string;
      city: string;
    };
  };
  orders: OrderModel[];
}
