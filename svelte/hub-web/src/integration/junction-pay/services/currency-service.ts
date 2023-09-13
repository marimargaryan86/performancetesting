import { currencyModel, type CurrencyModel, type CurrencySchema } from "../schemas/money";
import JunctionPayService from "./junction-pay-service";

export default class CurrencyService extends JunctionPayService {
  async listCurrencies(token: string): Promise<Map<string, CurrencyModel>> {
    const resp = await this.makeRequest<{
      data: CurrencySchema[];
      links: { next: string };
    }>("/currencies", {
      queryParams: { "page[limit]": 100 },
      token,
    });

    return new Map(
      resp.json.data.map((currency) => [currency.id, currencyModel.toModel(currency)]),
    );
  }
}
