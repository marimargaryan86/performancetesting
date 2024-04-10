import * as CommonSchemas from "~/integration/common/schemas";
import type { Order } from "./order";
import type { IncludedMapping } from "./included";
import type { Specification } from "./__generated__";
import type { PostCreatedResponse, PostRequest } from "~/integration/common/types";

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

export type MarkupsSchema = PostCreatedResponse<Specification, "/orders/markups">["data"];

export type MarkupsCreate = Pick<
  Markups,
  "orderId" | "serviceFee" | "agencyMarkup" | "totalToCollect"
>;

export type MarkupsCreateSchema = PostRequest<Specification, "/orders/markups">["data"];

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
