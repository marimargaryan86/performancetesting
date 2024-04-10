import type { GetOKResponse, PatchRequest } from "~/integration/common/types";
import type { IncludedMapping } from "./included";
import { moneyParser, type Money } from "./money";
import type { Order } from "./order";
import type { Specification } from "./__generated__";

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

export type BillSchema = GetOKResponse<Specification, "/bills">["data"][number];

export type BillUpdateSchema = PatchRequest<Specification, "/bills/{billId}">["data"];

export const billParser = {
  toModel: (data: BillSchema, included?: IncludedMapping): Bill => {
    const orderId = data.relationships?.order?.data.id;

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
