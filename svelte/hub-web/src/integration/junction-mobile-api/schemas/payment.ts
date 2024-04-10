import * as CommonSchemas from "~/integration/common/schemas";
import { z } from "zod";
import type { Specification } from "./__generated__";
import type { PostOKResponse, PostRequest } from "~/integration/common/types";

export const paymentModel = z.object({
  id: z.string(),
  clientSecret: z.string(),
  ephemeralKey: z.string().optional(),
  customerId: z.string().optional(),
});

export type Payment = z.infer<typeof paymentModel>;

export type PaymentSchema = NonNullable<PostOKResponse<Specification, "/payments">["data"]>;

type PaymentCreateSchema = PostRequest<Specification, "/payments">["data"];

export const paymentParser = {
  toModel: (data: PaymentSchema): Payment => {
    return {
      id: data.id,
      clientSecret: data.attributes.clientSecret,
      ephemeralKey: data.attributes.ephemeralKey,
      customerId: data.attributes.customerId,
    };
  },
  toCreateSchema: (data: CommonSchemas.Price): PaymentCreateSchema => ({
    type: "payments",
    attributes: CommonSchemas.priceParser.toSchema(data),
  }),
};

export type Voucher = {
  id: string;
};

export type VoucherSchema = {
  id: string;
  type: "vouchers";
};

export const voucherParser = {
  toModel: (data: VoucherSchema): Voucher => ({
    id: data.id,
  }),
};
