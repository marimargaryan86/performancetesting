import type { SessionModel } from "models/user";
import JunctionHubApiService from "./junction-hub-api-service";
import {
  balanceParser,
  type Balance,
  type BalanceSchema,
  type BalanceAdd,
} from "../schemas/balance";

export default class BalanceService extends JunctionHubApiService {
  async listBalances({
    session,
    accountId,
  }: {
    session: SessionModel;
    accountId: string;
  }): Promise<Balance[]> {
    const resp = await this.makeRequest<{ data: BalanceSchema[] }>(
      `/accounts/${accountId}/balances`,
      { session },
    );

    return resp.json.data.map((item) => balanceParser.toModel(item));
  }

  async addBalance({
    session,
    accountId,
    data,
  }: {
    session: SessionModel;
    accountId: string;
    data: BalanceAdd;
  }): Promise<Balance> {
    const resp = await this.makeRequest<{ data: BalanceSchema }>(
      `/accounts/${accountId}/relationships/currencies`,
      {
        method: "POST",
        data: { data: balanceParser.toAddSchema(data) },
        session,
      },
    );

    return balanceParser.toModel(resp.json.data);
  }
}
