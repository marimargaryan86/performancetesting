import { accountModel, type AccountModel, type AccountSchema } from "../schemas/account";
import JunctionPayService from "./junction-pay-service";
import type { PaginatedData } from "models/common";

export default class AccountService extends JunctionPayService {
  async listAccounts(token: string, cursor?: string): Promise<PaginatedData<AccountModel>> {
    const resp = await this.makeRequest<{ data: AccountSchema[]; links: { next: string } }>(
      "/accounts",
      {
        token,
        queryParams: { "page[cursor]": cursor },
      },
    );

    return {
      data: resp.json.data.map(accountModel.toModel),
      cursor: AccountService.getCursor(resp.json),
    };
  }

  async getAccount(token: string, accountId: string): Promise<AccountModel> {
    const resp = await this.makeRequest<{ data: AccountSchema }>(`/accounts/${accountId}`, {
      token,
    });

    return accountModel.toModel(resp.json.data);
  }
}
