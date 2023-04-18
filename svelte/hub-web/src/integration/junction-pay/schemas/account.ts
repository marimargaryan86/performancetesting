import type { RelationshipSchema } from "./common";
import type { CompanyIdentifierSchema } from "./company";
import type { ContactPersonIdentifierSchema } from "./contact-person";

export interface AccountIdentifierSchema {
  id: string;
  type: "accounts";
}

export interface AccountSchema extends AccountIdentifierSchema {
  attributes: {
    name: string;
    status: string;
  };
  relationships: {
    company?: RelationshipSchema<CompanyIdentifierSchema>;
    contactPerson?: RelationshipSchema<ContactPersonIdentifierSchema>;
  };
}

export interface ListAccountsResponseSchema {
  data: AccountSchema[];
  links: {
    next: string;
  };
}
