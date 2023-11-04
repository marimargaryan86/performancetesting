import {
  enhancedAddressDetailsParser,
  type EnhancedAddressDetails,
  type EnhancedAddressDetailsSchema,
} from "./address";
import type { IncludedMapping } from "./included";
import type { Order, OrderSchema } from "./order";

export type ContactDetails = {
  email: string;
  address: Required<Omit<EnhancedAddressDetails, "state">>;
  phone: string;
};

export type ContactDetailsSchema = {
  email: string;
  address: Required<Omit<EnhancedAddressDetailsSchema, "state">>;
  phoneNumber: string;
};

export const contactDetailsParser = {
  toModel: (data: ContactDetailsSchema): ContactDetails => ({
    email: data.email,
    address: enhancedAddressDetailsParser.toModel(data.address) as ContactDetails["address"],
    phone: data.phoneNumber,
  }),
};

export type Journey = {
  id: string;
  reference: string;
  contact: ContactDetails;
  orderIds: string[];
  orders: Order[];
};

export type JourneySchema = {
  id: string;
  type: "journeys";
  attributes: {
    reference: string;
    contactDetails: ContactDetailsSchema;
  };
  relationships: {
    orders: { data: Pick<OrderSchema, "id" | "type">[] };
  };
  links: { self: string };
};

export const journeyParser = {
  toModel: (data: JourneySchema, included?: IncludedMapping): Journey => {
    const orderIds = data.relationships.orders.data.map(({ id }) => id);

    return {
      id: data.id,
      reference: data.attributes.reference,
      contact: contactDetailsParser.toModel(data.attributes.contactDetails),
      orderIds,
      orders: included?.orders?.filter(({ id }) => orderIds.includes(id)) ?? [],
    };
  },
};
