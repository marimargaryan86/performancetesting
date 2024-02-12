import * as CommonSchemas from "~/integration/common/schemas";
import type { Order, OrderSchema } from "./order";
import type { IncludedMapping } from "./included";

export type Markups = {
  id: string;
  createdAt: Date;
  updatedAt: Date;
  serviceFee: CommonSchemas.Price;
  agencyMarkup: CommonSchemas.Price;
  totalToCollect: CommonSchemas.Price;
  orderId: string;
  order?: Order;
};

export type MarkupsSchema = {
  id: string;
  type: "markups";
  attributes: {
    serviceFee: CommonSchemas.PriceSchema;
    agencyMarkup: CommonSchemas.PriceSchema;
    totalToCollect: CommonSchemas.PriceSchema;
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
      serviceFee: CommonSchemas.priceParser.toModel(data.attributes.serviceFee),
      agencyMarkup: CommonSchemas.priceParser.toModel(data.attributes.agencyMarkup),
      totalToCollect: CommonSchemas.priceParser.toModel(data.attributes.totalToCollect),
      orderId,
      order: included?.orders?.find(({ id }) => id === orderId),
    };
  },
  toCreateSchema: (data: MarkupsCreate): MarkupsCreateSchema => ({
    type: "markups",
    attributes: {
      agencyMarkup: CommonSchemas.priceParser.toSchema(data.agencyMarkup),
      serviceFee: CommonSchemas.priceParser.toSchema(data.serviceFee),
      totalToCollect: CommonSchemas.priceParser.toSchema(data.totalToCollect),
    },
    relationships: { order: { data: { id: data.orderId, type: "orders" } } },
  }),
};
