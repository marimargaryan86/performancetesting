import {
  paymentIntentModel,
  createPaymentIntentModel,
  type PaymentIntentModel,
  type PaymentIntentSchema,
} from "../schemas/payment";
import JunctionMobileApiService from "./junction-mobile-api-service";
import type { PriceModel } from "../schemas/price";

export class PaymentService extends JunctionMobileApiService {
  async createPayment(data: PriceModel): Promise<PaymentIntentModel> {
    const resp = await this.makeRequest<{ data: PaymentIntentSchema }>("/payments", {
      method: "POST",
      data: { data: createPaymentIntentModel.toSchema(data) },
    });

    return paymentIntentModel.toModel(resp.json.data);
  }
}
