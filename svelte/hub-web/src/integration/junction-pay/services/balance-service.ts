import type { AddBalanceResponseSchema, ListBalancesResponseSchema } from "../schemas/balance";
import JunctionPayService from "./junction-pay-service";
import type { priceModel } from "integration/junction-mobile-api/schemas/price";
import type { Infer } from "integration/junction-mobile-api/schema-model.server";

export default class BalanceService extends JunctionPayService {
  async listBalances(token: string, accountId: string): Promise<Infer<typeof priceModel>[]> {
    const resp = await this.makeRequest<ListBalancesResponseSchema>(
      `/accounts/${accountId}/balances`,
      { token },
    );

    if (resp.status === 404) {
      return [];
    }

    if (resp.status !== 200) {
      throw new Error(`Junction Pay error: ${resp.status}`);
    }

    return (await resp.json()).data.map((item) => ({
      amount: item.attributes.amount,
      currency: item.relationships.currency.data.id,
    }));
  }

  async addBalance(
    token: string,
    accountId: string,
    currencyCode: string,
  ): Promise<Infer<typeof priceModel>> {
    const resp = await this.makeRequest<AddBalanceResponseSchema>(
      `/accounts/${accountId}/relationships/currencies`,
      {
        method: "POST",
        data: {
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
        },
        token,
      },
    );

    if (resp.status !== 201) {
      throw new Error(`Junction Pay error: ${resp.status}`);
    }

    const data = await resp.json();

    return {
      amount: data.data.attributes.amount,
      currency: data.data.relationships.currency.data.id,
    };
  }
}
