import type { CurrencyModel } from "models/money";
import type { ListCurrenciesResponseSchema } from "../schemas/money";
import JunctionPayService from "./junction-pay-service";

export default class CurrencyService extends JunctionPayService {
  async listCurrencies(token: string): Promise<CurrencyModel[]> {
    const resp = await fetch(this.getResourceUrl("/currencies", { "page[limit]": 100 }), {
      headers: this.getHeadersWithAuth(token),
    });

    if (resp.status !== 200) {
      throw new Error(`Junction Pay error: ${resp.status}`);
    }

    const data = (await resp.json()) as ListCurrenciesResponseSchema;
    return data.data.map((item) => ({
      code: item.id,
      minorUnits: item.attributes.minorUnits,
      name: item.attributes.name,
    }));
  }
}
