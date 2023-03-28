import type { MoneyModel } from "models/money";
import type { AddBalanceResponseSchema, ListBalancesResponseSchema } from "../schemas/balance";
import JunctionPayService from "./junction-pay-service";

export default class BalanceService extends JunctionPayService {
  async listBalances(token: string, accountId: string): Promise<MoneyModel[]> {
    const resp = await fetch(this.getResourceUrl(`/accounts/${accountId}/balances`), {
      headers: this.getHeadersWithAuth(token),
    });

    if (resp.status === 404) {
      return [];
    }

    if (resp.status !== 200) {
      throw new Error(`Junction Pay error: ${resp.status}`);
    }

    const data = (await resp.json()) as ListBalancesResponseSchema;

    return data.data.map((item) => ({
      amount: item.attributes.amount,
      currency: item.relationships.currency.data.id,
    }));
  }

  async addBalance(token: string, accountId: string, currencyCode: string): Promise<MoneyModel> {
    const resp = await fetch(
      this.getResourceUrl(`/accounts/${accountId}/relationships/currencies`),
      {
        method: "POST",
        headers: this.getHeadersWithAuth(token),
        body: JSON.stringify({
          data: {
            type: "balances",
            relationships: {
              currency: {
                data: {
                  id: currencyCode,
                  type: "currencies",
                },
              },
            },
          },
        }),
      },
    );

    if (resp.status !== 201) {
      throw new Error(`Junction Pay error: ${resp.status}`);
    }

    const data = (await resp.json()) as AddBalanceResponseSchema;

    return {
      amount: data.data.attributes.amount,
      currency: data.data.relationships.currency.data.id,
    };
  }
}
