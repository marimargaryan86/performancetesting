import type { SessionModel } from "models/user";
import { currencyModel, type CurrencyModel, type CurrencySchema } from "../schemas/money";
import JunctionHubApiService from "./junction-hub-api-service";

export default class CurrencyService extends JunctionHubApiService {
  async listCurrencies({
    session,
  }: {
    session: SessionModel;
  }): Promise<Map<string, CurrencyModel>> {
    const resp = await this.makeRequest<{
      data: CurrencySchema[];
      links: { next: string };
    }>("/currencies", {
      queryParams: { "page[limit]": 100 },
      session,
    });

    return new Map(
      resp.json.data.map((currency) => [currency.id, currencyModel.toModel(currency)]),
    );
  }
}
