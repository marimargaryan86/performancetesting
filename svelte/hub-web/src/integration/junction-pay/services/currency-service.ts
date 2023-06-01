import type { CurrencyModel } from "models/money";
import type { ListCurrenciesResponseSchema } from "../schemas/money";
import JunctionPayService from "./junction-pay-service";

export default class CurrencyService extends JunctionPayService {
  async listCurrencies(token: string): Promise<CurrencyModel[]> {
    const resp = await this.makeRequest<ListCurrenciesResponseSchema>("/currencies", {
      queryParams: { "page[limit]": 100 },
      token,
    });

    if (resp.status !== 200) {
      throw new Error(`Junction Pay error: ${resp.status}`);
    }

    return (await resp.json()).data.map((item) => ({
      code: item.id,
      minorUnits: item.attributes.minorUnits,
      name: item.attributes.name,
    }));
  }
}
