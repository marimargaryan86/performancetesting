import type { FindCriteriaModel } from "$integration/currency-cloud/models/beneficiaries/find";
import type { GetRequirementsModel } from "$integration/currency-cloud/models/beneficiaries/requirements";
import type { RecursivePartial } from "$models/common-models";
import type { BeneficiaryPutModel } from "$integration/currency-cloud/models/beneficiaries/common";
import type {
  CreateBeneficiarySchema,
  CreateCompanyBeneficiarySchema,
  CreateIndividualBeneficiarySchema,
  FindCriteriaSchema,
  GetRequirementsSchema,
  UpdateBeneficiarySchema,
} from "../schemas/beneficiaries";

export function parseCreateBeneficiarySchema(data: CreateBeneficiarySchema): BeneficiaryPutModel {
  return {
    bank: {
      account: {
        currencyCode: data.bank.account.currencyCode,
        holderName: data.bank.account.holderName,
        bic: data.bank.account.bic,
        iban: data.bank.account.iban,
        number: data.bank.account.number,
        sortCode: data.bank.account.sortCode,
        type: data.bank.account.type,
      },
      countryCode: data.bank.countryCode,
      address: data.bank.address,
      name: data.bank.name,
    },
    nickname: data.nickname,
    contact: {
      address: data.contact?.address,
      city: data.contact?.city,
      countryCode: data.contact?.countryCode,
      email: data.contact?.email,
      externalReference: data.contact?.externalReference,
      postalCode: data.contact?.postalCode,
      stateOrProvince: data.contact?.stateOrProvince,
    },
    default: data.default,
    identification: {
      type: data.identification?.type,
      value: data.identification?.value,
    },
    paymentTypes: data.paymentTypes,
    ...(data.entityType === "company"
      ? {
          entityType: "company",
          company: {
            name: data.company?.name,
            registrationDate:
              typeof data.company?.registrationDate === "string"
                ? new Date(data.company.registrationDate)
                : data.company?.registrationDate,
          },
        }
      : data.entityType === "individual"
      ? {
          entityType: "individual",
          individual: {
            birthDate:
              typeof data.individual?.birthDate === "string"
                ? new Date(data.individual.birthDate)
                : data.individual?.birthDate,
            firstName: data.individual?.firstName,
            lastName: data.individual?.lastName,
          },
        }
      : {
          entityType: data.entityType,
        }),
  };
}

export function parseUpdateBeneficiarySchema(
  data: UpdateBeneficiarySchema,
): RecursivePartial<BeneficiaryPutModel> {
  const { company } = data as CreateCompanyBeneficiarySchema;
  const { individual } = data as CreateIndividualBeneficiarySchema;

  return {
    bank: {
      account: {
        bic: data.bank?.account?.bic,
        currencyCode: data.bank?.account?.currencyCode,
        holderName: data.bank?.account?.holderName,
        iban: data.bank?.account?.iban,
        number: data.bank?.account?.number,
        sortCode: data.bank?.account?.sortCode,
        type: data.bank?.account?.type,
      },
      address: data.bank?.address,
      countryCode: data.bank?.countryCode,
      name: data.bank?.name,
    },
    company: {
      name: company?.name,
      registrationDate:
        typeof company?.registrationDate === "string"
          ? new Date(company.registrationDate)
          : company?.registrationDate,
    },
    individual: {
      birthDate:
        typeof individual?.birthDate === "string"
          ? new Date(individual.birthDate)
          : individual?.birthDate,
      firstName: individual?.firstName,
      lastName: individual?.lastName,
    },
    contact: {
      address: data.contact?.address,
      city: data.contact?.city,
      countryCode: data.contact?.countryCode,
      email: data.contact?.email,
      externalReference: data.contact?.externalReference,
      postalCode: data.contact?.postalCode,
      stateOrProvince: data.contact?.stateOrProvince,
    },
    default: data.default,
    identification: {
      type: data.identification?.type,
      value: data.identification?.value,
    },
    nickname: data.nickname,
    paymentTypes: data.paymentTypes,
    entityType: data.entityType,
  };
}

export function parseGetRequirementsSchema(data: GetRequirementsSchema): GetRequirementsModel {
  return {
    entityType: data.entityType,
    paymentTypes: data.paymentTypes,
    bank: {
      account: {
        countryCode: data.bankAccountCountryCode,
        currencyCode: data.bankAccountCurrencyCode,
      },
    },
    contact: {
      countryCode: data.contactCountryCode,
    },
  };
}

export function parseFindCriteriaSchema(data: FindCriteriaSchema): FindCriteriaModel {
  return {
    bank: {
      account: {
        bic: data.bankAccountBic,
        currencyCode: data.bankAccountCurrencyCode,
        holderName: data.bankAccountHolderName,
        iban: data.bankAccountIban,
        number: data.bankAccountNumber,
        sortCode: data.bankAccountSortCode,
        type: data.bankAccountType,
      },
      name: data.bankName,
    },
    contact: {
      city: data.contactCity,
      countryCode: data.contactCountryCode,
      externalReference: data.contactExternalReference,
      postalCode: data.contactPostalCode,
      stateOrProvince: data.contactStateOrProvince,
    },
    defaultBeneficiary: data.defaultBeneficiary,
    limit: data["page[limit]"],
    offset: data["page[offset]"],
    nickname: data.nickname,
    order: data["orderBy[asc]"] ?? data["orderBy[desc]"],
    orderDirection: data["orderBy[asc]"] ? "asc" : data["orderBy[desc]"] ? "desc" : "asc",
    scope: data.scope,
    ...(data.entityType === "company"
      ? {
          entityType: "company",
          company: {
            name: data.companyName,
            registrationDate: data.companyRegistrationDate
              ? new Date(data.companyRegistrationDate)
              : undefined,
          },
        }
      : data.entityType === "individual"
      ? {
          entityType: "individual",
          individual: {
            birthDate: data.individualBirthDate ? new Date(data.individualBirthDate) : undefined,
            firstName: data.individualFirstName,
            lastName: data.individualLastName,
          },
        }
      : undefined),
  };
}
