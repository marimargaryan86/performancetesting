import type { IncludedMapping } from "./included";
import { moneyParser, type Money, type MoneySchema } from "./money";
import type { Order, OrderSchema } from "./order";

export type Bill = {
  id: string;
  createdAt?: Date;
  updatedAt?: Date;
  reconciled: boolean;
  amounts: {
    total?: Money;
    reconciled?: Money;
  };
  orderId?: string;
  order?: Order;
};

export type BillSchema = {
  id: string;
  type: "bills";
  attributes?: {
    createdAt?: string;
    updatedAt?: string;
    isReconciled: boolean;
    totalAmount?: MoneySchema;
    reconciledAmount?: MoneySchema | null;
  };
  relationships: {
    order?: { data: Pick<OrderSchema, "id" | "type"> };
  };
  links: { self: string };
};

export type BillUpdateSchema = Pick<BillSchema, "type"> & {
  attributes?: {
    createdAt?: string;
    updatedAt?: string;
    isReconciled?: boolean;
  };
};

export const billParser = {
  toModel: (data: BillSchema, included?: IncludedMapping): Bill => {
    const orderId = data.relationships.order?.data.id;

    return {
      id: data.id,
      amounts: {
        total: data.attributes?.totalAmount
          ? moneyParser.toModel(data.attributes.totalAmount)
          : undefined,
        reconciled: data.attributes?.reconciledAmount
          ? moneyParser.toModel(data.attributes.reconciledAmount)
          : undefined,
      },
      reconciled: data.attributes?.isReconciled ?? false,
      createdAt: data.attributes?.createdAt ? new Date(data.attributes.createdAt) : undefined,
      updatedAt: data.attributes?.updatedAt ? new Date(data.attributes.updatedAt) : undefined,
      orderId,
      order: included?.orders?.find(({ id }) => id === orderId),
    };
  },
  toUpdateSchema: (data: Bill): BillUpdateSchema => ({
    type: "bills",
    attributes: {
      createdAt: data.createdAt?.toISOString(),
      updatedAt: data.createdAt?.toISOString(),
      isReconciled: data.reconciled,
    },
  }),
};
