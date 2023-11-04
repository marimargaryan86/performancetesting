import type { SessionModel } from "models/user";
import JunctionHubApiService from "./junction-hub-api-service";
import { currencyParser, type Currency, type CurrencySchema } from "../schemas/currency";

export default class CurrencyService extends JunctionHubApiService {
  async listCurrencies({ session }: { session: SessionModel }): Promise<Map<string, Currency>> {
    const resp = await this.makeRequest<{
      data: CurrencySchema[];
      links: { next: string };
    }>("/currencies", {
      queryParams: { "page[limit]": 100 },
      session,
    });

    return new Map(
      resp.json.data.map((currency) => [currency.id, currencyParser.toModel(currency)]),
    );
  }
}
