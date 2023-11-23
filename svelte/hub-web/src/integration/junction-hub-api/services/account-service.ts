import type { Session } from "integration/ory/schemas/authentication";
import JunctionHubApiService from "./junction-hub-api-service";
import type { PaginatedData } from "models/common";
import { accountParser, type Account, type AccountSchema } from "../schemas/account";

export default class AccountService extends JunctionHubApiService {
  async find({
    session,
    cursor,
    limit = 100,
  }: {
    session: Session;
    cursor?: string;
    limit?: number;
  }): Promise<PaginatedData<Account>> {
    const resp = await this.makeRequest<{ data: AccountSchema[]; links: { next: string } }>(
      "/accounts",
      {
        session,
        queryParams: { "page[cursor]": cursor, "page[limit]": limit },
      },
    );

    return {
      data: resp.json.data.map((item) => accountParser.toModel(item)),
      cursor: AccountService.getCursor(resp.json),
    };
  }

  async get({ session, id }: { session: Session; id: string }): Promise<Account> {
    const resp = await this.makeRequest<{ data: AccountSchema }>(`/accounts/${id}`, {
      session,
    });

    return accountParser.toModel(resp.json.data);
  }
}
