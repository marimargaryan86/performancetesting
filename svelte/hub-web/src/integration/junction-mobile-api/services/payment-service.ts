import JunctionMobileApiService from "./junction-mobile-api-service";
import type * as OrySchemas from "~/integration/ory/schemas";
import type * as CommonSchemas from "~/integration/common/schemas";
import { paymentParser, type Payment, type PaymentSchema } from "../schemas/payment";

export default class PaymentService extends JunctionMobileApiService {
  async create({
    session,
    data,
  }: {
    session: OrySchemas.Session;
    data: CommonSchemas.Price;
  }): Promise<Payment> {
    const resp = await this.makeRequest<{ data: PaymentSchema }>("/payments", {
      method: "POST",
      data: { data: paymentParser.toCreateSchema(data) },
      session,
    });

    return paymentParser.toModel(resp.json.data);
  }
}
