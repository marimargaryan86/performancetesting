import currencyMapping from "$content/currency-mapping";
import utils from "$lib/utils";
import type { BalanceModel } from "$models/balance-models";
import BaseService from "./base-service";
import type { BalancesResponse } from "./schemas/balance-schemas";

export default class BalanceService extends BaseService {
  async findBalances(limit = 20, offset = 1): Promise<BalanceModel[]> {
    try {
      const response = await fetch(
        utils.buildUrl(`${this.baseUrl}/balances`, {
          "page[cursor]": offset,
          "page[limit]": limit,
        }),
        {
          method: "GET",
        },
      );
      const data: BalancesResponse = await response.json();

      return data.data.map((item) => ({
        id: item.id,
        amount: item.attributes.amount,
        code: item.relationships.currency.data.id,
        name: currencyMapping[item.relationships.currency.data.id],
      }));
    } catch {
      throw new Error("An unexpected error occured");
    }
  }
}
