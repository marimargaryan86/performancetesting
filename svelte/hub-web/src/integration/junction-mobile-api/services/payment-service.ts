import type { PriceModel } from "models/booking/money";
import type { CreatePaymentRequestSchema, CreatePaymentResponseSchema } from "../schemas/payment";
import JunctionMobileApiService from "./junction-mobile-api-service";
import type { PaymentIntentModel } from "models/booking/payment";
import { parsePaymentIntentSchema } from "../parsers/payment";

export class PaymentService extends JunctionMobileApiService {
  async createPayment(data: PriceModel): Promise<PaymentIntentModel> {
    const resp = await this.makeRequest<CreatePaymentResponseSchema, CreatePaymentRequestSchema>(
      "/payments",
      {
        method: "POST",
        data: {
          data: {
            type: "payments",
            attributes: {
              amount: data.amount.toString(),
              currency: data.currency,
            },
          },
        },
      },
    );

    return parsePaymentIntentSchema((await resp.json()).data);
  }
}
