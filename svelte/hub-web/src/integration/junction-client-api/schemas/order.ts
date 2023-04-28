import type { BookingIdentifierSchema } from "./booking";
import type { RelationshipSchema } from "./common";
import type { JourneyIdentifierSchema } from "./journey";
import type { QuoteIdentifierSchema } from "./offer";

export interface OrderIdentifierSchema {
  id: string;
  type: "orders";
}

export interface OrderPassengerSchema {
  firstName: string;
  lastName: string;
  title: "unspecified" | "mr" | "mrs" | "ms" | "miss";
  gender: "unspecified" | "male" | "female";
  dateOfBirth: string;
  travelerDocument?: {
    documentType?: "passport";
    documentNumber?: string;
    documentIssueCountry?: string;
    documentExpirationDate?: string;
    documentIssueDate?: string;
    nationality?: string;
    residenceCountryCode?: string;
  };
}

export interface OrderSchema extends OrderIdentifierSchema {
  attributes: {
    passengers: OrderPassengerSchema[];
  };
  relationships: {
    quote: RelationshipSchema<QuoteIdentifierSchema>;
    journey: RelationshipSchema<JourneyIdentifierSchema>;
    bookings: RelationshipSchema<BookingIdentifierSchema>;
  };
  links: { self: string };
}
