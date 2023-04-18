import type { ConversionModel } from "models/conversion";
import type { GetConversionDetailsResponseSchema } from "../schemas/conversion";
import type { ListTransactionsResponseSchema } from "../schemas/transaction";
import JunctionPayService from "./junction-pay-service";

export default class ConversionService extends JunctionPayService {
  async listConversions(token: string): Promise<ConversionModel[]> {
    const transactions = (await (
      await this.makeRequest("/transactions", { token })
    ).json()) as ListTransactionsResponseSchema;
    const conversionIds = transactions.data.map((item) => item.relationships.conversion.data.id);

    return Promise.all(conversionIds.map((id) => this.getConversionDetails(id, token)));
  }

  async getConversionDetails(conversionId: string, token: string): Promise<ConversionModel> {
    const resp = await this.makeRequest(`/conversions/${conversionId}`, { token });

    if (resp.status !== 200) {
      throw new Error(`Junction Pay error: ${resp.status}`);
    }

    const data = (await resp.json()) as GetConversionDetailsResponseSchema;

    return {
      id: data.data.id,
      rate: data.data.attributes.rate,
      settledAt: new Date(data.data.attributes.settledAt),
    };
  }
}
