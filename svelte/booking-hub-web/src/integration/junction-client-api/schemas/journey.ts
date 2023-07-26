import type { RelationshipSchema } from "./common";
import type { OrderIdentifierSchema } from "./order";

export interface JourneyIdentifierSchema {
  id: string;
  type: "journeys";
}

export interface JourneySchema extends JourneyIdentifierSchema {
  attributes: {
    reference: string;
    contactDetails: {
      email: string;
      address: {
        addressLines: string[];
        countryCode: string;
        postalCode: string;
        city: string;
      };
      phoneNumber: string;
    };
  };
  relationships: {
    orders: RelationshipSchema<OrderIdentifierSchema[]>;
  };
  links: { self: string };
}
