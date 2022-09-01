import type { AccountModel, FindCriteriaModel } from "../models/accounts";
import { parseAccountSchema, parseFindCriteriaModel } from "../parsers/accounts";
import type { AccountSchema, FindAccountsResponseSchema } from "../schemas/accounts";
import BaseService from "./base-service";

export default class AccountService extends BaseService {
  async find(criteria: FindCriteriaModel): Promise<AccountModel[]> {
    const resp = await this.fetch("/v2/accounts/find", undefined, parseFindCriteriaModel(criteria));

    switch (resp.status) {
      case 200:
        break;
      default:
        throw "SERVICE_UNAVAILABLE";
    }

    const data: FindAccountsResponseSchema = await resp.json();

    return data.accounts.map((item) => parseAccountSchema(item));
  }

  async get(id: string): Promise<AccountModel> {
    const resp = await this.fetch(`/v2/accounts/${id}`);

    switch (resp.status) {
      case 200:
        break;
      default:
        throw "SERVICE_UNAVAILABLE";
    }

    const data: AccountSchema = await resp.json();

    return parseAccountSchema(data);
  }
}
