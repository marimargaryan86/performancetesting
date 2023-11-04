import type { SessionModel } from "models/user";
import JunctionHubApiService from "./junction-hub-api-service";
import type { PaginatedData } from "models/common";
import { accountParser, type Account, type AccountSchema } from "../schemas/account";

export default class AccountService extends JunctionHubApiService {
  async listAccounts({
    session,
    cursor,
  }: {
    session: SessionModel;
    cursor?: string;
  }): Promise<PaginatedData<Account>> {
    const resp = await this.makeRequest<{ data: AccountSchema[]; links: { next: string } }>(
      "/accounts",
      {
        session,
        queryParams: { "page[cursor]": cursor },
      },
    );

    return {
      data: resp.json.data.map((item) => accountParser.toModel(item)),
      cursor: AccountService.getCursor(resp.json),
    };
  }

  async getAccount({ session, id }: { session: SessionModel; id: string }): Promise<Account> {
    const resp = await this.makeRequest<{ data: AccountSchema }>(`/accounts/${id}`, {
      session,
    });

    return accountParser.toModel(resp.json.data);
  }
}
