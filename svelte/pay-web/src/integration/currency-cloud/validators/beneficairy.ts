import { removeUndefinedValues } from "../helpers";
import type { BeneficiaryPutModel } from "../models/beneficiaries/common";
import type { RequirementsModel } from "../models/beneficiaries/requirements";
import type { ValidationError } from "../models/common";
import {
  bankAccountTypes,
  entityTypes,
  identificationTypes,
  paymentTypes,
} from "../schemas/beneficiaries";
import {
  validateArray,
  validateBoolean,
  validateCountryCode,
  validateCurrencyCode,
  validateDate,
  validateEmail,
  validateEnum,
  validateLength,
  validateUUID,
} from "./common";

export function validateEntityType(
  value?: string | null,
  required = true,
  nullable = false,
): ValidationError<string> {
  return validateEnum(value, entityTypes, required, nullable);
}

export function validateAccountType(
  value?: string | null,
  required = true,
  nullable = false,
): ValidationError<string> {
  return validateEnum(value, bankAccountTypes, required, nullable);
}

export function validateIdentificationType(
  value?: string | null,
  required = true,
  nullable = false,
): ValidationError<string> {
  return validateEnum(value, identificationTypes, required, nullable);
}

export function validatePaymentType(value?: string, required = true): ValidationError<string> {
  return validateEnum(value, paymentTypes, required);
}

export function validatePaymentTypes(
  value?: string[],
  required = true,
): ValidationError<string[] | string> {
  return validateArray(value, (value) => validatePaymentType(value), required) as ValidationError<
    string[] | string
  >;
}

export function validateCompanyName(
  value?: string | null,
  required = true,
  nullable = false,
): ValidationError<string> {
  return validateLength(value, 1, 255, required, nullable);
}

export function validateAddress(
  value?: string | null,
  required = true,
  nullable = false,
): ValidationError<string> {
  return validateLength(value, 1, 255, required, nullable);
}

export function validateCity(
  value?: string | null,
  required = true,
  nullable = false,
): ValidationError<string> {
  return validateLength(value, 1, 255, required, nullable);
}

export function validateStateOrProvince(
  value?: string | null,
  required = true,
  nullable = false,
): ValidationError<string> {
  return validateLength(value, 1, 255, required, nullable);
}

export function validateHolderName(
  value?: string | null,
  required = true,
  nullable = false,
): ValidationError<string> {
  return validateLength(value, 1, 255, required, nullable);
}

export function validateNickname(
  value?: string,
  required = true,
  nullable = false,
): ValidationError<string> {
  return validateLength(value, 1, 255, required, nullable);
}

export function validateFirstName(
  value?: string | null,
  required = true,
  nullable = false,
): ValidationError<string> {
  return validateLength(value, 1, 255, required, nullable);
}

export function validateLastName(
  value?: string | null,
  required = true,
  nullable = false,
): ValidationError<string> {
  return validateLength(value, 1, 255, required, nullable);
}

export function validateIban(
  value?: string | null,
  required = true,
  nullable = false,
): ValidationError<string> {
  if (!nullable && value === null) {
    return ["Not nullable"];
  } else if (value === null) {
    return undefined;
  }

  if (value === undefined) {
    if (required) {
      return ["Missing"];
    }

    return undefined;
  }

  return value.match(/^([A-Z0-9]\s*){15,34}$/) ? undefined : ["Invalid IBAN format"];
}

export function validateBic(
  value?: string | null,
  required = true,
  nullable = false,
): ValidationError<string> {
  if (!nullable && value === null) {
    return ["Not nullable"];
  } else if (value === null) {
    return undefined;
  }

  if (value === undefined) {
    if (required) {
      return ["Missing"];
    }

    return undefined;
  }

  return value.match(/^[0-9A-Z]{8}$|^[0-9A-Z]{11}$/) ? undefined : ["Invalid BIC format"];
}

export function validateAccountNumber(
  value?: string | null,
  required = true,
  nullable = false,
): ValidationError<string> {
  if (!nullable && value === null) {
    return ["Not nullable"];
  } else if (value === null) {
    return undefined;
  }

  if (value === undefined) {
    if (required) {
      return ["Missing"];
    }

    return undefined;
  }

  return value.match(/^\d{8}$/) ? undefined : ["Invalid account number"];
}

export function validateSortCode(
  value?: string | null,
  required = true,
  nullable = false,
): ValidationError<string> {
  if (!nullable && value === null) {
    return ["Not nullable"];
  } else if (value === null) {
    return undefined;
  }

  if (value === undefined) {
    if (required) {
      return ["Missing"];
    }

    return undefined;
  }

  return value.match(/^\d{6}$/) ? undefined : ["Invalid sort code"];
}

export function validatePostalCode(
  value?: string | null,
  required = true,
  nullable = false,
): ValidationError<string> {
  return validateLength(value, 1, 12, required, nullable);
}

export function validateBankName(
  value?: string | null,
  required = true,
  nullable = false,
): ValidationError<string> {
  return validateLength(value, 1, 255, required, nullable);
}

export function validatePutModel(
  data: BeneficiaryPutModel,
  requirementsList: RequirementsModel[],
): BeneficiaryPutModel {
  let regularValid = data.paymentTypes?.includes("regular") ? false : true;
  let priorityValid = data.paymentTypes?.includes("priority") ? false : true;
  let entityValid = false;

  const errors = requirementsList
    .map((requirements) => {
      const { bic, iban, number, sortCode } = requirements.bank.account;
      const { address, city, countryCode, postalCode, stateOrProvince } = requirements.contact;

      if (
        (data.paymentTypes && !data.paymentTypes.includes(requirements.paymentType)) ||
        (data.entityType && data.entityType !== requirements.entityType)
      ) {
        return undefined;
      }

      const error = removeUndefinedValues<ValidationError<BeneficiaryPutModel>>({
        bank: {
          countryCode: validateCountryCode(data.bank.countryCode),
          account: {
            currencyCode: validateCurrencyCode(data.bank.account.currencyCode),
            holderName: validateHolderName(data.bank.account.holderName),
            bic: validateBic(data.bank.account.bic, bic, !bic),
            iban: validateIban(data.bank.account.iban, iban, !iban),
            number: validateAccountNumber(data.bank.account.number, number, !number),
            sortCode: validateSortCode(data.bank.account.sortCode, sortCode, !sortCode),
            type: validateAccountType(data.bank.account.type, false, true),
          },
          address: validateAddress(data.bank.address, false, true),
          name: validateBankName(data.bank.name, false, true),
        },
        default: validateBoolean(data.default, false),
        contact: {
          address: validateAddress(data.contact?.address, address, !address),
          city: validateCity(data.contact?.city, city, !city),
          countryCode: validateCountryCode(data.contact?.countryCode, countryCode, !countryCode),
          email: validateEmail(data.contact?.email, false, true),
          externalReference: validateLength(data.contact?.externalReference, 1, 255, false, true),
          postalCode: validatePostalCode(data.contact?.postalCode, postalCode, !postalCode),
          stateOrProvince: validateStateOrProvince(
            data.contact?.stateOrProvince,
            stateOrProvince,
            !stateOrProvince,
          ),
        },
        onBehalfOf: validateUUID(data.onBehalfOf, false, true),
        paymentTypes: validatePaymentTypes(data.paymentTypes, false),
        nickname: validateNickname(data.nickname),
        entityType: validateEntityType(data.entityType, false, true),
        identification: {
          type: validateIdentificationType(data.identification?.type, false, true),
          value: data.identification?.type
            ? validateLength(data.identification.value, 1, 255)
            : undefined,
        },
        company:
          data.entityType === "company"
            ? {
                name: validateCompanyName(data.company?.name),
                registrationDate: validateDate(data.company?.registrationDate),
              }
            : undefined,
        individual:
          data.entityType === "individual"
            ? {
                birthDate: validateDate(data.individual?.birthDate),
                firstName: validateFirstName(data.individual?.firstName),
                lastName: validateLastName(data.individual?.lastName),
              }
            : undefined,
      });

      if (!error) {
        regularValid = regularValid || requirements.paymentType === "regular";
        priorityValid = priorityValid || requirements.paymentType === "priority";
        entityValid = true;
      }

      return error;
    })
    .filter((item) => !!item);

  if (!(regularValid && priorityValid && entityValid)) {
    throw errors;
  }

  return data;
}
