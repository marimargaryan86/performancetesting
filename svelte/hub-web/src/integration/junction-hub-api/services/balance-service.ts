import type { SessionModel } from "models/user";
import { balanceModel, createBalanceModel, type BalanceSchema } from "../schemas/balance";
import JunctionHubApiService from "./junction-hub-api-service";
import type { PriceModel } from "integration/junction-mobile-api/schemas/price";

export default class BalanceService extends JunctionHubApiService {
  async listBalances({
    session,
    accountId,
  }: {
    session: SessionModel;
    accountId: string;
  }): Promise<PriceModel[]> {
    const resp = await this.makeRequest<{ data: BalanceSchema[] }>(
      `/accounts/${accountId}/balances`,
      { session },
    );

    return resp.json.data.map(balanceModel.toModel);
  }

  async addBalance({
    session,
    accountId,
    currencyCode,
  }: {
    session: SessionModel;
    accountId: string;
    currencyCode: string;
  }): Promise<PriceModel> {
    const resp = await this.makeRequest<{ data: BalanceSchema }>(
      `/accounts/${accountId}/relationships/currencies`,
      {
        method: "POST",
        data: { data: createBalanceModel.toSchema({ currencyCode }) },
        session,
      },
    );

    return balanceModel.toModel(resp.json.data);
  }
}
