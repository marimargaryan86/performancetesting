import * as CommonSchemas from "~/integration/common/schemas";
import type { IncludedMapping } from "./included";
import type { Order, OrderSchema } from "./order";
import type { DateRange } from "$lib/models/date-time";
import type { BookingStatus } from "./booking";

export type ContactDetails = {
  email: string;
  address: Required<Omit<CommonSchemas.EnhancedAddressDetails, "state">>;
  phone: string;
};

export type ContactDetailsSchema = {
  email: string;
  address: Required<Omit<CommonSchemas.EnhancedAddressDetailsSchema, "state">>;
  phoneNumber: string;
};

export const contactDetailsParser = {
  toModel: (data: ContactDetailsSchema): ContactDetails => ({
    email: data.email,
    address: CommonSchemas.enhancedAddressDetailsParser.toModel(
      data.address,
    ) as ContactDetails["address"],
    phone: data.phoneNumber,
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

export type JourneySchema = {
  id: string;
  type: "journeys";
  attributes: {
    createdAt: string;
    reference: string;
    contactDetails: ContactDetailsSchema;
  };
  relationships: {
    orders: { data: Pick<OrderSchema, "id" | "type">[] };
  };
  links: { self: string };
};

export type JourneyFilterOptions = {
  departureAtRange?: DateRange;
  createdAtRange?: DateRange;
  bookingStatus?: BookingStatus;
  passengerLastName?: string;
  passengerNameRecord?: string;
};

export type JourneyFilterOptionsQuery = {
  "departureAt[from]"?: string;
  "departureAt[to]"?: string;
  "createdAt[from]"?: string;
  "createdAt[to]"?: string;
  bookingStatus?: string;
  passengerLastName?: string;
  passengerNameRecord?: string;
};

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
