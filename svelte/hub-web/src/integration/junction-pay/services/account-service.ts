import type { AccountModel } from "models/account";
import type { ListAccountsResponseSchema } from "../schemas/account";
import JunctionPayService from "./junction-pay-service";

export default class AccountService extends JunctionPayService {
  async listAccounts(token: string): Promise<AccountModel[]> {
    const resp = await this.makeRequest("/accounts", { token });

    if (resp.status !== 200) {
      throw new Error(`Junction Pay error: ${resp.status}`);
    }

    const data = (await resp.json()) as ListAccountsResponseSchema;
    const result = data.data.map((item) => ({
      headAccount: false,
      id: item.id,
      name: item.attributes.name,
      companyId: item.relationships.company?.data.id,
      contactPersonId: item.relationships.contactPerson?.data.id,
    }));

    return result;
  }

  async getAccount(token: string, accountId: string): Promise<AccountModel> {
    const accounts = await this.listAccounts(token);
    const account = accounts.find((item) => item.id === accountId);

    if (!account) {
      throw new Error("Junction Pay error: account not found");
    }

    return account;
  }
}
