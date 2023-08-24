import type { PaymentIntentModel } from "models/booking/payment";
import type { PaymentIntentSchema } from "../schemas/payment";

export function parsePaymentIntentSchema(data: PaymentIntentSchema): PaymentIntentModel {
  return {
    id: data.id,
    clientSecret: data.attributes.clientSecret,
    customerId: data.attributes.customerId,
    ephemeralKey: data.attributes.ephemeralKey,
  };
}
