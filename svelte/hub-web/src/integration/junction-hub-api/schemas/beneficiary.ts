import { z } from "zod";
import { accountModel } from "./account";
import { currencyModel } from "./money";
import {
  getSchemaModel,
  links,
  relationship,
  type Infer,
} from "integration/common/schema-model.server";
import {
  addressDetails as addressDetailsClient,
  enhancedAddressDetails as enhancedAddressDetailsClient,
  bankDetailsBase as bankDetailsBaseModelClient,
  bankDetailsIban as bankDetailsIbanClient,
  bankDetailsAba as bankDetailsAbaClient,
  bankDetails as bankDetailsClient,
  beneficiaryModel as beneficiaryModelClient,
} from "./beneficiary.client";

const addressDetails = getSchemaModel(
  z.object({
    addressLines: z.array(z.string()),
    countryCode: z.string(),
  }),
  addressDetailsClient,
);

export const enhancedAddressDetails = getSchemaModel(
  addressDetails.schema.extend({
    postalCode: z.string().optional(),
    city: z.string().optional(),
    state: z.string().nullable().optional(),
  }),
  enhancedAddressDetailsClient,
  {
    toModel: (data) => ({
      addressLines: data.addressLines,
      countryCode: data.countryCode,
      city: data.city ?? "",
      postalCode: data.postalCode ?? "",
      state: data.state ?? undefined,
    }),
    toSchema: (data) => ({
      addressLines: data.addressLines,
      countryCode: data.countryCode,
      city: data.city,
      postalCode: data.postalCode,
      state: data.state,
    }),
  },
);

export const bankDetailsBase = getSchemaModel(
  z.object({
    name: z.string(),
    bicSwift: z.string().nullable().optional(),
    accountType: z.enum(["checking", "savings"]),
    paymentTypes: z.enum(["priority", "regular"]),
    address: addressDetails.schema,
  }),
  bankDetailsBaseModelClient,
);

export const bankDetailsAba = getSchemaModel(
  bankDetailsBase.schema.extend({
    accountNumber: z.string().nullable(),
    aba: z.string().nullable(),
  }),
  bankDetailsAbaClient,
);

export const bankDetailsIban = getSchemaModel(
  bankDetailsBase.schema.extend({
    iban: z.string().nullable(),
  }),
  bankDetailsIbanClient,
);

export const bankDetails = getSchemaModel(
  z.union([bankDetailsAba.schema, bankDetailsIban.schema]),
  bankDetailsClient,
  {
    toModel: (data) => {
      const base = {
        accountType: data.accountType,
        address: data.address,
        name: data.name,
        paymentType: data.paymentTypes,
        bicSwift: data.bicSwift ?? "",
      };

      if ("accountNumber" in data) {
        return {
          ...base,
          type: "aba" as const,
          accountNumber: data.accountNumber as string,
          aba: data.aba as string,
        };
      }

      return { ...base, type: "iban" as const, iban: data.iban as string };
    },
    toSchema: (data) => ({
      bicSwift: data.bicSwift,
      accountType: data.accountType,
      name: data.name,
      address: {
        addressLines: data.address.addressLines,
        countryCode: data.address.countryCode,
      },
      paymentTypes: data.paymentType,
      ...(data.type === "aba"
        ? { aba: data.aba, accountNumber: data.accountNumber }
        : { iban: data.iban }),
    }),
  },
);

export const beneficiaryModel = getSchemaModel(
  z.object({
    id: z.string(),
    type: z.enum(["beneficiaries"]),
    attributes: z.object({
      bankAccountHolderName: z.string(),
      email: z.string(),
      beneficiaryAddress: enhancedAddressDetails.schema,
      bankDetails: bankDetails.schema,
    }),
    relationships: relationship({
      currency: currencyModel.identifier,
      account: accountModel.identifier,
    }),
    links: links(["self"]),
  }),
  beneficiaryModelClient,
  {
    toModel: (data) => ({
      id: data.id,
      companyName: data.attributes.bankAccountHolderName,
      email: data.attributes.email,
      address: enhancedAddressDetails.toModel(data.attributes.beneficiaryAddress),
      bankDetails: bankDetails.toModel(data.attributes.bankDetails),
      accountId: data.relationships.account.data.id,
      currencyCode: data.relationships.currency.data.id,
    }),
  },
);
export type BeneficiaryModel = Infer<typeof beneficiaryModel>;
export type BeneficiarySchema = Infer<typeof beneficiaryModel, "schema">;

export const putBeneficiaryModel = getSchemaModel(
  beneficiaryModel.schema.omit({ id: true, links: true }),
  beneficiaryModel.model.omit({ id: true }),
  {
    toSchema: (data) => ({
      type: "beneficiaries" as const,
      attributes: {
        bankAccountHolderName: data.companyName,
        bankDetails: bankDetails.toSchema(data.bankDetails),
        beneficiaryAddress: enhancedAddressDetails.toSchema(data.address),
        email: data.email,
      },
      relationships: {
        account: { data: { type: "accounts" as const, id: data.accountId } },
        currency: { data: { type: "currencies" as const, id: data.currencyCode } },
      },
    }),
  },
);
