import * as CommonSchemas from "~/integration/common/schemas";
import type { GetOKResponse, PostRequest } from "~/integration/common/types";
import type * as OrySchemas from "~/integration/ory/schemas";
import type { Specification } from "./__generated__";

export type Reseller = {
  id: string;
  name?: string;
  providers?: string[];

  // TODO(2024-03-11/alvin.s): fix typing.
  company?: NonNullable<ResellerSchema["relationships"]>["company"];
  currency?: NonNullable<ResellerSchema["relationships"]>["currency"];
  parentResellers?: NonNullable<ResellerSchema["relationships"]>["parentResellers"];
};

export type ResellerSchema = NonNullable<
  GetOKResponse<Specification, "/resellers/{resellerId}">["data"]
>;

export const resellerParser = {
  toModel: (data: ResellerSchema): Reseller => ({
    id: data.id,
    name: data.attributes.name,
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

export type UserPut = Omit<User, "id">;

export type UserSchema = GetOKResponse<Specification, "/users/{userId}">["data"];

export type UserPutSchema = PostRequest<Specification, "/users">["data"];

export const userParser = {
  toModel: (data: UserSchema): User => ({
    id: data.id,
    email: data.attributes.email,
    role: data.attributes.role,
    resellerId: data.relationships.reseller?.data.id,
    // TODO: include?
    reseller: undefined,
  }),
  toPutSchema: (data: UserPut): UserPutSchema => ({
    type: "users",
    attributes: {
      email: data.email,
      role: data.role,
    },
    relationships: {
      reseller: data.resellerId ? { data: { id: data.resellerId, type: "resellers" } } : null,
    },
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

export type UserProfileSchema = GetOKResponse<Specification, "/users/me">["data"];

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
