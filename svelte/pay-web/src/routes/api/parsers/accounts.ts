import type { FindCriteriaModel } from "$integration/currency-cloud/models/accounts";
import type { FindCriteriaSchema } from "../schemas/accounts";

export function parseFindCriteriaSchema(data: FindCriteriaSchema): FindCriteriaModel {
  return {
    bankAccountVerificationStatus: data.bankAccountVerificationStatus,
    brand: data.brand,
    contact: {
      address: data.contactAddress,
      city: data.contactCity,
      countryCode: data.contactCountryCode,
      postalCode: data.contactPostalCode,
      stateOrProvince: data.contactStateOrProvince,
    },
    limit: data["page[limit]"],
    name: data.name,
    offset: data["page[offset]"],
    order: data["orderBy[asc]"] ?? data["orderBy[desc]"],
    orderDirection: data["orderBy[asc]"] ? "asc" : data["orderBy[desc]"] ? "desc" : "asc",
    ref: data.ref,
    spreadTable: data.spreadTable,
    status: data.status,
  };
}
