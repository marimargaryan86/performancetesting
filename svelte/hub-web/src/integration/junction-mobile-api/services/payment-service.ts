import { paymentIntentModel, createPaymentIntentModel } from "../schemas/payment";
import JunctionMobileApiService from "./junction-mobile-api-service";
import type { Infer } from "../schema-model.server";
import type { priceModel } from "../schemas/price";

export class PaymentService extends JunctionMobileApiService {
  async createPayment(data: Infer<typeof priceModel>): Promise<Infer<typeof paymentIntentModel>> {
    const resp = await this.makeRequest<
      { data: Infer<typeof paymentIntentModel, "schema"> },
      { data: Infer<typeof createPaymentIntentModel, "schema"> }
    >("/payments", {
      method: "POST",
      data: { data: createPaymentIntentModel.toSchema(data) },
    });

    return paymentIntentModel.toModel((await resp.json()).data);
  }
}
