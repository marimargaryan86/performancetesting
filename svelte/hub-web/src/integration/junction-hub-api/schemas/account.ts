import type { CompanySchema, Company } from "./company";
import type { Contact, ContactSchema } from "./contact";
import type { IncludedMapping } from "./included";

export type Account = {
  id: string;
  name: string;
  status: "enabled" | "disabled";
  companyId?: string;
  company?: Company;
  contactId?: string;
  contact?: Contact;
};

export type AccountCreate = Pick<Account, "name" | "contactId">;

export type AccountSchema = {
  id: string;
  type: "accounts";
  attributes: {
    name: string;
    status: "enabled" | "disabled";
  };
  relationships: {
    company: { data: Pick<CompanySchema, "id" | "type"> | null };
    contact: { data: Pick<ContactSchema, "id" | "type"> | null };
  };
  links: { self: string };
};

export type AccountUpdateSchema = Pick<AccountSchema, "type"> & {
  attributes: Pick<AccountSchema["attributes"], "status">;
};

export type AccountCreateSchema = Pick<AccountSchema, "type"> & {
  attributes: Pick<AccountSchema["attributes"], "name">;
  relationships: Pick<AccountSchema["relationships"], "contact">;
};

export const accountParser = {
  toModel: (data: AccountSchema, included?: IncludedMapping): Account => {
    const companyId = data.relationships.company.data?.id ?? undefined;
    const contactId = data.relationships.contact.data?.id ?? undefined;

    return {
      id: data.id,
      name: data.attributes.name,
      status: data.attributes.status,
      companyId,
      company: included?.companies?.find(({ id }) => id === companyId),
      contactId,
      contact: included?.contacts?.find(({ id }) => id === contactId),
    };
  },
  toUpdateSchema: (data: Account): AccountUpdateSchema => ({
    type: "accounts",
    attributes: { status: data.status },
  }),
  toCreateSchema: (data: AccountCreate): AccountCreateSchema => ({
    type: "accounts",
    attributes: { name: data.name },
    relationships: {
      contact: { data: data.contactId ? { id: data.contactId, type: "contacts" } : null },
    },
  }),
};
