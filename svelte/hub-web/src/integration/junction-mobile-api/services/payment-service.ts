import JunctionMobileApiService from "./junction-mobile-api-service";
import type { Session } from "integration/ory/schemas/authentication";
import type { Price } from "integration/common/schemas/price";
import { paymentParser, type Payment, type PaymentSchema } from "../schemas/payment";

export default class PaymentService extends JunctionMobileApiService {
  async create({ session, data }: { session: Session; data: Price }): Promise<Payment> {
    const resp = await this.makeRequest<{ data: PaymentSchema }>("/payments", {
      method: "POST",
      data: { data: paymentParser.toCreateSchema(data) },
      session,
    });

    return paymentParser.toModel(resp.json.data);
  }
}
