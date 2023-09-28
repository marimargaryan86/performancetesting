import type { SessionModel } from "models/user";
import { accountModel, type AccountModel, type AccountSchema } from "../schemas/account";
import JunctionHubApiService from "./junction-hub-api-service";
import type { PaginatedData } from "models/common";

export default class AccountService extends JunctionHubApiService {
  async listAccounts({
    session,
    cursor,
  }: {
    session: SessionModel;
    cursor?: string;
  }): Promise<PaginatedData<AccountModel>> {
    const resp = await this.makeRequest<{ data: AccountSchema[]; links: { next: string } }>(
      "/accounts",
      {
        session,
        queryParams: { "page[cursor]": cursor },
      },
    );

    return {
      data: resp.json.data.map(accountModel.toModel),
      cursor: AccountService.getCursor(resp.json),
    };
  }

  async getAccount({ session, id }: { session: SessionModel; id: string }): Promise<AccountModel> {
    const resp = await this.makeRequest<{ data: AccountSchema }>(`/accounts/${id}`, {
      session,
    });

    return accountModel.toModel(resp.json.data);
  }
}
