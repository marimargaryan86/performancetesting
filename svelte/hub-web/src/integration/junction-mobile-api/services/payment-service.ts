import {
  paymentIntentModel,
  createPaymentIntentModel,
  type PaymentIntentModel,
  type PaymentIntentSchema,
} from "../schemas/payment";
import JunctionMobileApiService from "./junction-mobile-api-service";
import type { PriceModel } from "../schemas/price";
import type { SessionModel } from "models/user";

export class PaymentService extends JunctionMobileApiService {
  async createPayment({
    session,
    data,
  }: {
    session: SessionModel;
    data: PriceModel;
  }): Promise<PaymentIntentModel> {
    const resp = await this.makeRequest<{ data: PaymentIntentSchema }>("/payments", {
      method: "POST",
      data: { data: createPaymentIntentModel.toSchema(data) },
      session,
    });

    return paymentIntentModel.toModel(resp.json.data);
  }
}
