import type { RecursivePartial, ValidationError } from "$integration/currency-cloud/models/common";
import {
  validateEntityType,
  validatePaymentTypes,
} from "$integration/currency-cloud/validators/beneficairy";
import {
  validateCountryCode,
  validateCurrencyCode,
} from "$integration/currency-cloud/validators/common";
import utils from "$lib/utils";
import type { GetRequirementsSchema } from "../../schemas/beneficiaries";

export function validateGetRequirementsSchema(
  data: RecursivePartial<GetRequirementsSchema>,
): GetRequirementsSchema {
  const errors = utils.removeUndefinedValues<ValidationError<GetRequirementsSchema>>({
    bankAccountCountryCode: validateCountryCode(data.bankAccountCountryCode),
    bankAccountCurrencyCode: validateCurrencyCode(data.bankAccountCurrencyCode),
    contactCountryCode: validateCountryCode(data.contactCountryCode, false),
    entityType: validateEntityType(data.entityType, false),
    paymentTypes: validatePaymentTypes(data.paymentTypes, false),
  });

  if (errors) {
    throw errors;
  }

  return data as GetRequirementsSchema;
}
