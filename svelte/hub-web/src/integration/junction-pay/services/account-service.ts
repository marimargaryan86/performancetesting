import type { AccountModel } from "models/account";
import type { GetAccountResponseSchema, ListAccountsResponseSchema } from "../schemas/account";
import JunctionPayService from "./junction-pay-service";
import { parseAccount } from "../parsers/account";
import type { PaginatedData } from "models/common";

export default class AccountService extends JunctionPayService {
  async listAccounts(token: string, cursor?: string): Promise<PaginatedData<AccountModel>> {
    const resp = await this.makeRequest("/accounts", {
      token,
      queryParams: { "page[cursor]": cursor },
    });

    if (resp.status !== 200) {
      throw new Error(`Junction Pay error: ${resp.status}`);
    }

    const data = (await resp.json()) as ListAccountsResponseSchema;

    return {
      data: data.data.map(parseAccount),
      cursor: AccountService.getCursor(data),
    };
  }

  async getAccount(token: string, accountId: string): Promise<AccountModel> {
    const resp = await this.makeRequest(`/accounts/${accountId}`, { token });

    if (resp.status !== 200) {
      throw new Error(`Junction Pay error: ${resp.status}`);
    }

    const data = (await resp.json()) as GetAccountResponseSchema;

    return parseAccount(data.data);
  }
}
