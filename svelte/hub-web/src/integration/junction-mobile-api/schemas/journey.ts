import * as CommonSchemas from "~/integration/common/schemas";
import type { IncludedMapping } from "./included";
import type { Order } from "./order";
import type { Specification } from "./__generated__";
import type { GetIncluded, GetOKResponse } from "~/integration/common/types";

export type ContactDetails = {
  email: string;
  address: Required<Omit<CommonSchemas.EnhancedAddressDetails, "state">>;
  phone: string;
};

export type ContactDetailsSchema = JourneySchema["attributes"]["contactDetails"];

export const contactDetailsParser = {
  toModel: (data: ContactDetailsSchema): ContactDetails => ({
    email: data.email,
    address: CommonSchemas.enhancedAddressDetailsParser.toModel(
      data.address,
    ) as ContactDetails["address"],
    phone: data.phoneNumber,
  }),
  toSchema: (data: ContactDetails): ContactDetailsSchema => ({
    email: data.email,
    address: CommonSchemas.enhancedAddressDetailsParser.toSchema(
      data.address,
    ) as ContactDetailsSchema["address"],
    phoneNumber: data.phone,
  }),
};

export type Journey = {
  id: string;
  createdAt: Date;
  reference: string;
  contact: ContactDetails;
  orderIds: string[];
  orders: Order[];
};

export type JourneySchema = GetIncluded<GetOKResponse<Specification, "/orders">, "journeys">;

export const journeyParser = {
  toModel: (data: JourneySchema, included?: IncludedMapping): Journey => {
    const orderIds = data.relationships.orders.data.map(({ id }) => id);

    return {
      id: data.id,
      createdAt: new Date(data.attributes.createdAt),
      reference: data.attributes.reference,
      contact: contactDetailsParser.toModel(data.attributes.contactDetails),
      orderIds,
      orders: included?.orders?.filter(({ id }) => orderIds.includes(id)) ?? [],
    };
  },
};
