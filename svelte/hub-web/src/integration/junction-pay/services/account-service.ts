import type { AccountModel } from "models/account";
import type { ListAccountsResponseSchema } from "../schemas/account";
import JunctionPayService from "./junction-pay-service";

export default class AccountService extends JunctionPayService {
  async listAccounts(token: string): Promise<AccountModel[]> {
    const resp = await fetch(this.getResourceUrl("/accounts"), {
      headers: this.getHeadersWithAuth(token),
    });

    if (resp.status !== 200) {
      throw new Error(`Junction Pay error: ${resp.status}`);
    }

    const data = (await resp.json()) as ListAccountsResponseSchema;

    return data.data.map((item) => ({
      headAccount: false,
      id: item.id,
      name: item.attributes.name,
    }));
  }
}
