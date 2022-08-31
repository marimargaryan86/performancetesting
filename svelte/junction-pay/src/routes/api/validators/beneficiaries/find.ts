import type { RecursivePartial, ValidationError } from "$integration/currency-cloud/models/common";
import { removeUndefinedValues } from "$integration/currency-cloud/helpers";
import { scopeTypes } from "$integration/currency-cloud/schemas/beneficiaries";
import {
  validateAccountNumber,
  validateAccountType,
  validateBankName,
  validateBic,
  validateCity,
  validateCompanyName,
  validateEntityType,
  validateFirstName,
  validateHolderName,
  validateIban,
  validateLastName,
  validateNickname,
  validatePostalCode,
  validateSortCode,
  validateStateOrProvince,
} from "$integration/currency-cloud/validators/beneficairy";
import {
  validateBoolean,
  validateCountryCode,
  validateCurrencyCode,
  validateDate,
  validateEnum,
  validateLength,
  validateNumber,
} from "$integration/currency-cloud/validators/common";
import type { FindCriteriaSchema } from "../../schemas/beneficiaries";
import { orderFields } from "$integration/currency-cloud/models/beneficiaries/find";

export function validateFindCriteriaSchema(
  data: RecursivePartial<FindCriteriaSchema>,
): FindCriteriaSchema {
  const errors = removeUndefinedValues<ValidationError<FindCriteriaSchema>>({
    "orderBy[asc]": validateEnum(data["orderBy[asc]"], orderFields, false),
    "orderBy[desc]": validateEnum(data["orderBy[desc]"], orderFields, false),
    "page[limit]": validateNumber(data["page[limit]"], 1, 25, false),
    "page[offset]": validateNumber(data["page[offset]"], 0, undefined, false),
    bankAccountBic: validateBic(data.bankAccountBic, false),
    bankAccountCurrencyCode: validateCurrencyCode(data.bankAccountCurrencyCode, false),
    bankAccountHolderName: validateHolderName(data.bankAccountHolderName, false),
    bankAccountIban: validateIban(data.bankAccountIban, false),
    bankAccountNumber: validateAccountNumber(data.bankAccountNumber, false),
    bankAccountSortCode: validateSortCode(data.bankAccountSortCode, false),
    bankAccountType: validateAccountType(data.bankAccountType, false),
    bankName: validateBankName(data.bankName, false),
    companyName: validateCompanyName(data.companyName, false),
    companyRegistrationDate: validateDate(data.companyRegistrationDate, false),
    contactCity: validateCity(data.contactCity, false),
    contactCountryCode: validateCountryCode(data.contactCountryCode, false),
    contactExternalReference: validateLength(data.contactExternalReference, 1, 255, false),
    contactPostalCode: validatePostalCode(data.contactPostalCode, false),
    contactStateOrProvince: validateStateOrProvince(data.contactStateOrProvince, false),
    defaultBeneficiary: validateBoolean(data.defaultBeneficiary, false),
    entityType: validateEntityType(data.entityType, false),
    individualBirthDate: validateDate(data.individualBirthDate, false),
    individualFirstName: validateFirstName(data.individualFirstName, false),
    individualLastName: validateLastName(data.individualLastName, false),
    nickname: validateNickname(data.nickname, false),
    scope: validateEnum(data.scope, scopeTypes, false),
  });

  if (errors) {
    throw errors;
  }

  return data as FindCriteriaSchema;
}
