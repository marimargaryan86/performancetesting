import type { RelationshipSchema } from "integration/common/schemas";
import type { ContactDetailsSchema, OrderIdentifierSchema } from "./order";

export interface JourneyIdentifierSchema {
  id: string;
  type: "journeys";
}

export interface JourneySchema extends JourneyIdentifierSchema {
  attributes: {
    reference: string;
    contactDetails: ContactDetailsSchema;
  };
  relationships: {
    orders: RelationshipSchema<OrderIdentifierSchema[]>;
  };
  links: { self: string };
}
