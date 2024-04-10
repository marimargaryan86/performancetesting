import type { GetOKResponse, PostRequest } from "~/integration/common/types";
import type { Company } from "./company";
import type { IncludedMapping } from "./included";
import type { Specification } from "./__generated__";

export type Contact = {
  id: string;
  firstName: string;
  lastName: string;
  email: string;
  phone: string;
  companyId: string;
  company?: Company;
};

export type ContactCreate = Omit<Contact, "id" | "companyId" | "company">;

export type ContactSchema = GetOKResponse<
  Specification,
  "/companies/{companyId}/contacts"
>["data"][number];

export type ContactCreateSchema = PostRequest<
  Specification,
  "/companies/{companyId}/contacts"
>["data"];

export const contactParser = {
  toModel: (data: ContactSchema, included?: IncludedMapping): Contact => {
    const companyId = data.relationships.company.data.id;

    return {
      id: data.id,
      firstName: data.attributes.firstName,
      lastName: data.attributes.lastName,
      email: data.attributes.emailAddress,
      phone: data.attributes.phoneNumber,
      companyId,
      company: included?.companies?.find(({ id }) => id === companyId),
    };
  },
  toCreateSchema: (data: ContactCreate): ContactCreateSchema => ({
    type: "contacts",
    attributes: {
      firstName: data.firstName,
      lastName: data.lastName,
      emailAddress: data.email,
      phoneNumber: data.phone,
    },
  }),
};
