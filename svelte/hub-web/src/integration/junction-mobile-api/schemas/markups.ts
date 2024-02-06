import { priceParser, type Price, type PriceSchema } from "~/integration/common/schemas/price";
import type { Order, OrderSchema } from "./order";
import type { IncludedMapping } from "./included";

export type Markups = {
  id: string;
  createdAt: Date;
  updatedAt: Date;
  serviceFee: Price;
  agencyMarkup: Price;
  totalToCollect: Price;
  orderId: string;
  order?: Order;
};

export type MarkupsSchema = {
  id: string;
  type: "markups";
  attributes: {
    serviceFee: PriceSchema;
    agencyMarkup: PriceSchema;
    totalToCollect: PriceSchema;
    createdAt: string;
    updatedAt: string;
  };
  relationships: {
    order: { data: Pick<OrderSchema, "id" | "type"> };
  };
};

export type MarkupsCreate = Pick<
  Markups,
  "orderId" | "serviceFee" | "agencyMarkup" | "totalToCollect"
>;

export type MarkupsCreateSchema = Pick<MarkupsSchema, "type" | "relationships"> & {
  attributes: Pick<MarkupsSchema["attributes"], "serviceFee" | "agencyMarkup" | "totalToCollect">;
};

export const markupsParser = {
  toModel: (data: MarkupsSchema, included?: IncludedMapping): Markups => {
    const orderId = data.relationships.order.data.id;

    return {
      id: data.id,
      createdAt: new Date(data.attributes.createdAt),
      updatedAt: new Date(data.attributes.updatedAt),
      serviceFee: priceParser.toModel(data.attributes.serviceFee),
      agencyMarkup: priceParser.toModel(data.attributes.agencyMarkup),
      totalToCollect: priceParser.toModel(data.attributes.totalToCollect),
      orderId,
      order: included?.orders?.find(({ id }) => id === orderId),
    };
  },
  toCreateSchema: (data: MarkupsCreate): MarkupsCreateSchema => ({
    type: "markups",
    attributes: {
      agencyMarkup: priceParser.toSchema(data.agencyMarkup),
      serviceFee: priceParser.toSchema(data.serviceFee),
      totalToCollect: priceParser.toSchema(data.totalToCollect),
    },
    relationships: { order: { data: { id: data.orderId, type: "orders" } } },
  }),
};
