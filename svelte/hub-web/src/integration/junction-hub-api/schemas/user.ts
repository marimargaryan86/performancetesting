import * as CommonSchemas from "~/integration/common/schemas";

export type User = {
  id: string;
};

export type UserSchema = {
  id: string;
  type: "users";
  attributes: unknown;
};

export const userParser = {
  toModel: (data: UserSchema): User => ({
    id: data.id,
  }),
};

export type UserProfile = {
  id: string;
  company: {
    name: string;
    address: CommonSchemas.EnhancedAddressDetails;
  };
  contacts: {
    firstName: string;
    lastName: string;
    email: string;
    phone: string;
  }[];
};

export type UserProfileSchema = {
  id: string;
  type: "users-profiles";
  attributes: {
    company: {
      name: string;
      address: CommonSchemas.EnhancedAddressDetailsSchema;
    };
    contacts: {
      firstName: string;
      lastName: string;
      emailAddress: string;
      phoneNumber: string;
    }[];
  };
};

export const userProfileParser = {
  toModel: (data: UserProfileSchema): UserProfile => ({
    id: data.id,
    company: {
      name: data.attributes.company.name,
      address: CommonSchemas.enhancedAddressDetailsParser.toModel(data.attributes.company.address),
    },
    contacts: data.attributes.contacts.map((item) => ({
      firstName: item.firstName,
      lastName: item.lastName,
      email: item.emailAddress,
      phone: item.phoneNumber,
    })),
  }),
};
