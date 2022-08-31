import { removeUndefinedValues } from "$integration/currency-cloud/helpers";
import type { ValidationError, RecursivePartial } from "$integration/currency-cloud/models/common";
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
import type {
  CreateCompanyBeneficiarySchema,
  CreateIndividualBeneficiarySchema,
  UpdateBeneficiarySchema,
} from "../../schemas/beneficiaries";

export function validateUpdateBeneficiarySchema(
  data: UpdateBeneficiarySchema,
): UpdateBeneficiarySchema {
  const { company } = data as RecursivePartial<CreateCompanyBeneficiarySchema>;
  const { individual } = data as RecursivePartial<CreateIndividualBeneficiarySchema>;

  const errors = removeUndefinedValues<ValidationError<UpdateBeneficiarySchema>>({
    bank: {
      account: {
        currencyCode: validateCurrencyCode(data.bank?.account?.currencyCode, false),
        holderName: validateHolderName(data.bank?.account?.holderName, false),
        bic: validateBic(data.bank?.account?.bic, false, true),
        iban: validateIban(data.bank?.account?.iban, false, true),
        number: validateAccountNumber(data.bank?.account?.number, false, true),
        sortCode: validateSortCode(data.bank?.account?.sortCode, false, true),
        type: validateAccountType(data.bank?.account?.type, false, true),
      },
      countryCode: validateCountryCode(data.bank?.countryCode, false),
      address: validateAddress(data.bank?.address, false, true),
      name: validateBankName(data.bank?.name, false, true),
    },
    contact: {
      address: validateAddress(data.contact?.address, false, true),
      city: validateCity(data.contact?.city, false, true),
      countryCode: validateCountryCode(data.contact?.countryCode, false, true),
      email: validateEmail(data.contact?.email, false, true),
      externalReference: validateLength(data.contact?.externalReference, 1, 255, false, true),
      postalCode: validatePostalCode(data.contact?.postalCode, false, true),
      stateOrProvince: validateStateOrProvince(data.contact?.stateOrProvince, false, true),
    },
    default: validateBoolean(data.default, false),
    entityType: validateEntityType(data.entityType, false, true),
    identification: {
      type: validateIdentificationType(data.identification?.type, false, true),
      value: validateLength(data.identification?.value, 1, 255, false, true),
    },
    nickname: validateNickname(data.nickname, false),
    paymentTypes: validatePaymentTypes(data.paymentTypes, false),
    company: {
      name: validateCompanyName(company?.name, false, true),
      registrationDate: validateDate(company?.registrationDate, false, true),
    },
    individual: {
      birthDate: validateDate(individual?.birthDate, false, true),
      firstName: validateFirstName(individual?.firstName, false, true),
      lastName: validateLastName(individual?.lastName, false, true),
    },
  });

  if (errors) {
    throw errors;
  }

  return data as UpdateBeneficiarySchema;
}
