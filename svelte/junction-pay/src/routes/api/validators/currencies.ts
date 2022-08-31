import { removeUndefinedValues } from "$integration/currency-cloud/helpers";
import type { ValidationError } from "$integration/currency-cloud/models/common";
import { orderFields } from "$integration/currency-cloud/models/currencies";
import { validateEnum, validateNumber } from "$integration/currency-cloud/validators/common";
import type { FindCriteriaSchema } from "../schemas/currencies";

export function validateFindCriteriaSchema(data: FindCriteriaSchema): FindCriteriaSchema {
  const errors = removeUndefinedValues<ValidationError<FindCriteriaSchema>>({
    "order[asc]": validateEnum(data["order[asc]"], orderFields, false),
    "order[desc]": validateEnum(data["order[desc]"], orderFields, false),
    "page[limit]": validateNumber(data["page[limit]"], 1, 20, false),
    "page[offset]": validateNumber(data["page[offset]"], 0, undefined, false),
  });

  if (errors) {
    throw errors;
  }

  return data;
}
