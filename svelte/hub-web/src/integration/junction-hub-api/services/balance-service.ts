import type { SessionModel } from "models/user";
import JunctionHubApiService from "./junction-hub-api-service";
import {
  balanceParser,
  type Balance,
  type BalanceSchema,
  type BalanceAdd,
} from "../schemas/balance";

export default class BalanceService extends JunctionHubApiService {
  async find({
    session,
    accountId,
    cursor,
    limit = 100,
  }: {
    session: SessionModel;
    accountId: string;
    cursor?: string;
    limit?: number;
  }): Promise<Balance[]> {
    const resp = await this.makeRequest<{ data: BalanceSchema[] }>(
      `/accounts/${accountId}/balances`,
      { session, queryParams: { "page[cursor]": cursor, "page[limit]": limit } },
    );

    return resp.json.data.map((item) => balanceParser.toModel(item));
  }

  async create({
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
