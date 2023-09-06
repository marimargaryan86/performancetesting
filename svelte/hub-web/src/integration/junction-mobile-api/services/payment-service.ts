import {
  paymentIntentModel,
  createPaymentIntentModel,
  type PaymentIntentModel,
  type PaymentIntentSchema,
  type CreatePaymentIntentSchema,
} from "../schemas/payment";
import JunctionMobileApiService from "./junction-mobile-api-service";
import type { PriceModel } from "../schemas/price";

export class PaymentService extends JunctionMobileApiService {
  async createPayment(data: PriceModel): Promise<PaymentIntentModel> {
    const resp = await this.makeRequest<
      { data: PaymentIntentSchema },
      { data: CreatePaymentIntentSchema }
    >("/payments", {
      method: "POST",
      data: { data: createPaymentIntentModel.toSchema(data) },
    });

    return paymentIntentModel.toModel((await resp.json()).data);
  }
}
