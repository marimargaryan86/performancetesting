import { balanceModel, createBalanceModel, type BalanceSchema } from "../schemas/balance";
import JunctionPayService from "./junction-pay-service";
import type { PriceModel } from "integration/junction-mobile-api/schemas/price";

export default class BalanceService extends JunctionPayService {
  async listBalances(token: string, accountId: string): Promise<PriceModel[]> {
    const resp = await this.makeRequest<{ data: BalanceSchema[] }>(
      `/accounts/${accountId}/balances`,
      { token },
    );

    if (resp.status !== 200) {
      throw new Error(`Junction Pay error: ${resp.status}`);
    }

    return (await resp.json()).data.map(balanceModel.toModel);
  }

  async addBalance(token: string, accountId: string, currencyCode: string): Promise<PriceModel> {
    const resp = await this.makeRequest<{ data: BalanceSchema }>(
      `/accounts/${accountId}/relationships/currencies`,
      {
        method: "POST",
        data: { data: createBalanceModel.toSchema({ currencyCode }) },
        token,
      },
    );

    if (resp.status !== 201) {
      throw new Error(`Junction Pay error: ${resp.status}`);
    }

    return balanceModel.toModel((await resp.json()).data);
  }
}
