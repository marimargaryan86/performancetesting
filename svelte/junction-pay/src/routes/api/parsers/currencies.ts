import type { FindCriteriaModel } from "$integration/currency-cloud/models/currencies";
import type { FindCriteriaSchema } from "../schemas/currencies";

export function parseFindCriteriaSchema(data: FindCriteriaSchema): FindCriteriaModel {
  return {
    limit: data["page[limit]"],
    offset: data["page[offset]"],
    order: data["order[asc]"] ?? data["order[desc]"],
    orderDirection: data["order[asc]"] ? "asc" : data["order[desc]"] ? "desc" : "asc",
  };
}
