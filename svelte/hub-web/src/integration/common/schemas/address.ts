import { ensureDefined } from "~/utils/array";

export type AddressSchema = {
  addressLines?: string[];
  countryCode?: string;
};

export type Address = {
  street?: {
    line1: string;
    line2?: string;
  };
  countryCode?: string;
};

export const addressParser = {
  toModel: (data: AddressSchema): Address => ({
    street: data.addressLines?.[0]
      ? {
          line1: data.addressLines[0],
          line2: data.addressLines[1],
        }
      : undefined,
    countryCode: data.countryCode,
  }),
  toSchema: (data: Address): AddressSchema => ({
    addressLines: data.street
      ? [data.street.line1, data.street.line2].filter(ensureDefined)
      : undefined,
    countryCode: data.countryCode,
  }),
};

export type EnhancedAddressDetailsSchema = AddressSchema & {
  postalCode?: string;
  city?: string;
  state?: string | null;
};

export type EnhancedAddressDetails = Address & {
  postalCode?: string;
  city?: string;
  state?: string;
};

export const enhancedAddressDetailsParser = {
  toModel: (data: EnhancedAddressDetailsSchema): EnhancedAddressDetails => ({
    ...addressParser.toModel(data),
    postalCode: data.postalCode,
    city: data.city,
    state: data.state ?? undefined,
  }),
  toSchema: (data: EnhancedAddressDetails): EnhancedAddressDetailsSchema => ({
    ...addressParser.toSchema(data),
    postalCode: data.postalCode,
    city: data.city,
    state: "state" in data ? data.state ?? null : undefined,
  }),
};
