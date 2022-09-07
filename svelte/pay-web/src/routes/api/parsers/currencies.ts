import type { FindCriteriaModel } from "$integration/currency-cloud/models/currencies";
import type { FindCriteriaSchema } from "../schemas/currencies";

export function parseFindCriteriaSchema(data: FindCriteriaSchema): FindCriteriaModel {
  return {
    limit: data["page[limit]"],
    offset: data["page[offset]"],
    order: data["orderBy[asc]"] ?? data["orderBy[desc]"],
    orderDirection: data["orderBy[asc]"] ? "asc" : data["orderBy[desc]"] ? "desc" : "asc",
  };
}
