import type { PriceSchema } from "./price";

export interface PaymentIntentSchema {
  id: string;
  type: "payments";
  attributes: {
    clientSecret: string;
    ephemeralKey?: string;
    customerId?: string;
  };
}

export interface CreatePaymentRequestSchema {
  data: {
    type: "payments";
    attributes: PriceSchema;
  };
}

export interface CreatePaymentResponseSchema {
  data: PaymentIntentSchema;
}
