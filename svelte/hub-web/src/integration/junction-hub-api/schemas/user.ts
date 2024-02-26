import * as CommonSchemas from "~/integration/common/schemas";
import type * as OrySchemas from "~/integration/ory/schemas";

export type Reseller = {
  id: string;
};

export type ResellerSchema = {
  id: string;
  type: "resellers";
};

export type User = {
  id: string;
  email: string;
  role: OrySchemas.UserRole;
  resellerId?: string;
  reseller?: Reseller;
};

export type UserCreate = Omit<User, "id">;

export type UserUpdate = UserCreate;

export type UserSchema = {
  id: string;
  type: "users";
  attributes: {
    email: string;
    role: OrySchemas.UserRole;
  };
  relationships: {
    reseller?: { data: Pick<ResellerSchema, "id" | "type"> } | null;
  };
};

export type UserCreateSchema = Omit<UserSchema, "id">;

export type UserUpdateSchema = UserCreateSchema;

export const userParser = {
  toModel: (data: UserSchema): User => ({
    id: data.id,
    email: data.attributes.email,
    role: data.attributes.role,
    // Check if reseller is neither null nor undefined before accessing id
    resellerId:
      data.relationships.reseller && data.relationships.reseller.data
        ? data.relationships.reseller.data.id
        : undefined,
    // TODO: include?
    reseller: undefined,
  }),
  toCreateSchema: (data: UserCreate): UserCreateSchema => ({
    type: "users",
    attributes: {
      email: data.email,
      role: data.role,
    },
    relationships: {
      reseller: data.resellerId ? { data: { id: data.resellerId, type: "resellers" } } : undefined,
    },
  }),
  get toUpdateSchema(): (data: UserUpdate) => UserUpdateSchema {
    return this.toCreateSchema;
  },
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
