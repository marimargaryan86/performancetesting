import type { AccountModel } from "models/account";
import type { AccountSchema } from "../schemas/account";

export function parseAccount(account: AccountSchema): AccountModel {
  return {
    headAccount: false,
    id: account.id,
    name: account.attributes.name,
    companyId: account.relationships.company?.data.id,
    contactPersonId: account.relationships.contactPerson?.data.id,
  };
}
