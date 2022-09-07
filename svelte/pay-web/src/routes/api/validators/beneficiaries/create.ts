import { removeUndefinedValues } from "$integration/currency-cloud/helpers";
import type { RecursivePartial, ValidationError } from "$integration/currency-cloud/models/common";
import {
  validateAccountNumber,
  validateAccountType,
  validateAddress,
  validateBankName,
  validateBic,
  validateCity,
  validateCompanyName,
  validateEntityType,
  validateFirstName,
  validateHolderName,
  validateIban,
  validateIdentificationType,
  validateLastName,
  validateNickname,
  validatePaymentTypes,
  validatePostalCode,
  validateSortCode,
  validateStateOrProvince,
} from "$integration/currency-cloud/validators/beneficairy";
import {
  validateBoolean,
  validateCountryCode,
  validateCurrencyCode,
  validateDate,
  validateEmail,
  validateLength,
} from "$integration/currency-cloud/validators/common";
import type { CreateBeneficiarySchema } from "../../schemas/beneficiaries";

export function validateCreateBeneficiarySchema(
  data: RecursivePartial<CreateBeneficiarySchema>,
): CreateBeneficiarySchema {
  const errors = removeUndefinedValues<ValidationError<CreateBeneficiarySchema>>({
    bank: {
      account: {
        currencyCode: validateCurrencyCode(data.bank?.account?.currencyCode),
        holderName: validateHolderName(data.bank?.account?.holderName),
        iban: validateIban(data.bank?.account?.iban, false),
        bic: validateBic(data.bank?.account?.bic, false),
        number: validateAccountNumber(data.bank?.account?.number, false),
        sortCode: validateSortCode(data.bank?.account?.sortCode, false),
        type: validateAccountType(data.bank?.account?.type, false),
      },
      countryCode: validateCountryCode(data.bank?.countryCode),
      address: validateAddress(data.bank?.address, false),
      name: validateBankName(data.bank?.name, false),
    },
    company:
      data.entityType === "company"
        ? data.company
          ? {
              name: validateCompanyName(data.company?.name),
              registrationDate: validateDate(data.company?.registrationDate),
            }
          : undefined
        : undefined,
    individual:
      data.entityType === "individual"
        ? data.individual
          ? {
              birthDate: validateDate(data.individual?.birthDate),
              firstName: validateFirstName(data.individual?.firstName),
              lastName: validateLastName(data.individual?.lastName),
            }
          : undefined
        : undefined,
    contact: data.contact
      ? {
          address: validateAddress(data.contact.address, false),
          city: validateCity(data.contact.city, false),
          countryCode: validateCountryCode(data.contact.countryCode, false),
          email: validateEmail(data.contact.email, false),
          externalReference: validateLength(data.contact.externalReference, 1, 255, false),
          postalCode: validatePostalCode(data.contact.postalCode, false),
          stateOrProvince: validateStateOrProvince(data.contact.stateOrProvince, false),
        }
      : undefined,
    default: validateBoolean(data.default, false),
    entityType: validateEntityType(data.entityType, false),
    identification: data.identification?.type
      ? {
          type: validateIdentificationType(data.identification?.type),
          value: validateLength(data.identification?.value, 1, 255),
        }
      : undefined,
    nickname: validateNickname(data.nickname),
    paymentTypes: validatePaymentTypes(data.paymentTypes, false),
  });

  if (errors) {
    throw errors;
  }

  return data as CreateBeneficiarySchema;
}
