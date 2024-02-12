import { z } from "zod";
import type * as HubSchemas from "~/integration/junction-hub-api/schemas";

export const refundDataModel = z.discriminatedUnion("type", [
  z.object({
    type: z.literal("automatic"),
    externalReference: z.string().trim().min(1).optional(),
    us: z.number().min(0),
    reseller: z.number().min(0),
  }),
  z.object({
    type: z.literal("manual"),
    externalReference: z.string().trim().min(1),
    us: z.number().min(0).optional(),
    reseller: z.number().min(0).optional(),
  }),
]);

export type RefundData = z.infer<typeof refundDataModel>;

export function getRefundPutData(
  data: RefundData,
  transaction: HubSchemas.Transaction,
): HubSchemas.RefundPut {
  return data.type === "automatic"
    ? {
        type: "automatic",
        transactionId: transaction.id,
        invoiceReference: transaction.invoiceReference ?? "",
        externalReference: data.externalReference,
        received: true,
        refunded: {
          reseller: {
            currency: transaction.amounts.quotation.currency,
            amount: data.reseller ?? 0,
          },
          us: {
            currency: transaction.amounts.beneficiary.currency,
            amount: data.us ?? 0,
          },
        },
        note: "",
      }
    : {
        type: "manual",
        externalReference: data.externalReference,
      };
}
