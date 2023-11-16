import type { Session } from "integration/ory/schemas";
import JunctionHubApiService from "./junction-hub-api-service";
import { currencyParser, type Currency, type CurrencySchema } from "../schemas/currency";
import type { PaginatedData } from "models/common";

export default class CurrencyService extends JunctionHubApiService {
  async find({
    session,
    cursor,
    limit = 100,
  }: {
    session: Session;
    cursor?: string;
    limit?: number;
  }): Promise<PaginatedData<Currency>> {
    const resp = await this.makeRequest<{
      data: CurrencySchema[];
      links: { next: string };
    }>("/currencies", {
      queryParams: { "page[limit]": limit, "page[cursor]": cursor },
      session,
    });

    return {
      data: resp.json.data.map(currencyParser.toModel),
      cursor: CurrencyService.getCursor(resp.json),
    };
  }
}
