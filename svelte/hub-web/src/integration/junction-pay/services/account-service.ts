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

    if (resp.status !== 200) {
      throw new Error(`Junction Pay error: ${resp.status}`);
    }

    const data = await resp.json();

    return {
      data: data.data.map(accountModel.toModel),
      cursor: AccountService.getCursor(data),
    };
  }

  async getAccount(token: string, accountId: string): Promise<AccountModel> {
    const resp = await this.makeRequest<{ data: AccountSchema }>(`/accounts/${accountId}`, {
      token,
    });

    if (resp.status !== 200) {
      throw new Error(`Junction Pay error: ${resp.status}`);
    }

    return accountModel.toModel((await resp.json()).data);
  }
}
