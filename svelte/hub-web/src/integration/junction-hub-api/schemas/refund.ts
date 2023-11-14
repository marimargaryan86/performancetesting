import type { Conversion, ConversionSchema } from "./conversion";
import type { IncludedMapping } from "./included";
import { moneyParser, type Money, type MoneySchema } from "./money";
import type { Transaction, TransactionSchema } from "./transaction";

export type RefundPosition = {
  id: string;
  total?: Money;
};

export type RefundPositionSchema = {
  id: string;
  type: "refund-position";
  attributes: {
    refundPosition?: MoneySchema;
  };
};

export type RefundPositionCreate = {
  refunded: {
    us: Money;
    reseller: Money;
  };
};

export type RefundPositionCreateSchema = Pick<RefundPositionSchema, "type"> & {
  attributes: {
    refundedUs: MoneySchema;
    refundedReseller: MoneySchema;
  };
};

export const refundPositionParser = {
  toModel: (data: RefundPositionSchema): RefundPosition => ({
    id: data.id,
    total: data.attributes.refundPosition
      ? moneyParser.toModel(data.attributes.refundPosition)
      : undefined,
  }),
  toCreateSchema: (data: RefundPositionCreate): RefundPositionCreateSchema => ({
    type: "refund-position",
    attributes: {
      refundedReseller: moneyParser.toSchema(data.refunded.reseller),
      refundedUs: moneyParser.toSchema(data.refunded.us),
    },
  }),
};

export type Refund = {
  id: string;
  status: "unspecified" | "pending" | "succeeded" | "failed";
  received: boolean;
  note: string;
  refunded: {
    us?: Money;
    usInPayerCurrency?: Money;
    reseller?: Money;
  };
  invoiceReference: string;
  externalReference?: string;
  transactionId?: string;
  transaction?: Transaction;
  conversionId?: string;
  conversion?: Conversion;
  refundPosition?: MoneySchema;
};

export type RefundPut =
  | (Pick<
      Refund,
      "received" | "note" | "invoiceReference" | "externalReference" | "transactionId"
    > & {
      type: "automatic";
      refunded: Pick<Refund["refunded"], "reseller" | "us">;
    })
  | (Required<Pick<Refund, "externalReference">> & { type: "manual" });

export type RefundSchema = {
  id: string;
  type: "refunds";
  attributes: {
    status: "unspecified" | "pending" | "succeeded" | "failed";
    refundReceived: boolean;
    note: string;
    refundedUs: MoneySchema | null;
    refundedUsInPayerCurrency?: MoneySchema | null;
    refundedReseller: MoneySchema | null;
    refundPosition?: MoneySchema | null;
    invoiceReference: string;
    externalReference?: string;
  };
  relationships: {
    transaction: { data?: Pick<TransactionSchema, "id" | "type"> };
    conversion?: { data?: Pick<ConversionSchema, "id" | "type"> | null };
  };
  links: { self: string };
};

export type RefundPutSchema = Pick<RefundSchema, "type"> &
  (
    | {
        attributes: Omit<RefundSchema["attributes"], "status" | "refundedUsInPayerCurrency">;
        relationships: Pick<RefundSchema["relationships"], "transaction">;
      }
    | {
        attributes: Pick<RefundSchema["attributes"], "externalReference">;
      }
  );

export const refundParser = {
  toModel: (data: RefundSchema, included?: IncludedMapping): Refund => {
    const transactionId = data.relationships.transaction.data?.id ?? undefined;
    const conversionId = data.relationships.conversion?.data?.id ?? undefined;

    return {
      id: data.id,
      status: data.attributes.status,
      received: data.attributes.refundReceived,
      note: data.attributes.note,
      refunded: {
        us: data.attributes.refundedUs
          ? moneyParser.toModel(data.attributes.refundedUs)
          : undefined,
        usInPayerCurrency: data.attributes.refundedUsInPayerCurrency
          ? moneyParser.toModel(data.attributes.refundedUsInPayerCurrency)
          : undefined,
        reseller: data.attributes.refundedReseller
          ? moneyParser.toModel(data.attributes.refundedReseller)
          : undefined,
      },
      invoiceReference: data.attributes.invoiceReference,
      externalReference: data.attributes.externalReference,
      transactionId,
      transaction: included?.transactions?.find(({ id }) => id === transactionId),
      conversionId,
      conversion: included?.conversions?.find(({ id }) => id === conversionId),
      refundPosition: data.attributes.refundPosition
        ? moneyParser.toModel(data.attributes.refundPosition)
        : undefined,
    };
  },
  toPutSchema: (data: RefundPut): RefundPutSchema => {
    if (data.type === "automatic") {
      return {
        type: "refunds",
        attributes: {
          refundReceived: data.received,
          note: data.note,
          refundedUs: data.refunded.us ? moneyParser.toSchema(data.refunded.us) : null,
          refundedReseller: data.refunded.reseller
            ? moneyParser.toSchema(data.refunded.reseller)
            : null,
          invoiceReference: data.invoiceReference,
          externalReference: data.externalReference,
        },
        relationships: {
          transaction: {
            data: data.transactionId ? { id: data.transactionId, type: "transactions" } : undefined,
          },
        },
      };
    }

    return {
      type: "refunds",
      attributes: { externalReference: data.externalReference },
    };
  },
};
