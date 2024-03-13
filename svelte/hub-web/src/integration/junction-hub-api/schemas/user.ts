import * as CommonSchemas from "~/integration/common/schemas";
import type * as OrySchemas from "~/integration/ory/schemas";

export type Reseller = {
  id: string;
  name?: string;
  providers?: string[];

  // TODO(2024-03-11/alvin.s): fix `unknown` typing.
  company?: unknown;
  currency?: unknown;
  parentResellers?: unknown;
};

export type ResellerSchema = {
  id: string;
  type: "resellers";
  attributes: {
    name?: string;
    providers?: string[];
  };
  relationships: {
    company?: unknown;
    currency?: unknown;
    parentResellers?: unknown;
  };
};

export const resellerParser = {
  toModel: (data: ResellerSchema): Reseller => ({
    id: data.id,
    name: data.attributes?.name,
    providers: data.attributes?.providers,
    company: data.relationships?.company,
    currency: data.relationships?.currency,
    parentResellers: data.relationships?.parentResellers,
  }),
  toSchema: (data: Reseller): ResellerSchema => ({
    id: data.id,
    type: "resellers",
    attributes: {
      name: data.name,
      providers: data.providers,
    },
    relationships: {
      company: data.company,
      currency: data.currency,
      parentResellers: data.parentResellers,
    },
  }),
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
