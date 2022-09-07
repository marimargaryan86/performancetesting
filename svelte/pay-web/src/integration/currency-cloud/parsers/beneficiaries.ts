import { thisOrThat } from "../helpers";
import type { BeneficiaryModel, BeneficiaryPutModel } from "../models/beneficiaries/common";
import { orderFieldMapping, type FindCriteriaModel } from "../models/beneficiaries/find";
import type { GetRequirementsModel, RequirementsModel } from "../models/beneficiaries/requirements";
import type { RecursivePartial } from "../models/common";
import type {
  BeneficiaryPutSchema,
  BeneficiarySchema,
  FindCriteriaSchema,
  GetRequirementsSchema,
  RequirementsSchema,
} from "../schemas/beneficiaries";

export function parseBeneficiarySchema(data: BeneficiarySchema): BeneficiaryModel {
  return {
    id: data.id,
    createdAt: new Date(data.created_at),
    modifiedAt: new Date(data.updated_at),
    nickname: data.name,
    paymentTypes: data.payment_types,
    identification: {
      type: data.beneficiary_identification_type,
      value: data.beneficiary_identification_value,
    },
    default: data.default_beneficiary === "true",
    contact: {
      address: data.beneficiary_address,
      city: data.beneficiary_city,
      countryCode: data.beneficiary_country,
      email: data.email,
      externalReference: data.beneficiary_external_reference,
      postalCode: data.beneficiary_postcode,
      stateOrProvince: data.beneficiary_state_or_province,
    },
    bank: {
      account: {
        bic: data.bic_swift,
        currencyCode: data.currency,
        holderName: data.bank_account_holder_name,
        iban: data.iban,
        number: data.account_number,
        sortCode:
          data.routing_code_type_1 === "sort_code"
            ? data.routing_code_value_1
            : data.routing_code_type_2 === "sort_code"
            ? data.routing_code_value_2
            : null,
        type: data.bank_account_type,
      },
      address: data.bank_address,
      countryCode: data.bank_country,
      name: data.bank_name,
    },
    creatorId: data.creator_contact_id,
    ...(data.beneficiary_entity_type === "company"
      ? {
          entityType: "company",
          company: {
            name: data.beneficiary_company_name,
            registrationDate: data.beneficiary_date_of_birth
              ? new Date(data.beneficiary_date_of_birth)
              : null,
          },
        }
      : data.beneficiary_entity_type === "individual"
      ? {
          entityType: "individual",
          individual: {
            birthDate: data.beneficiary_date_of_birth
              ? new Date(data.beneficiary_date_of_birth)
              : null,
            firstName: data.beneficiary_first_name,
            lastName: data.beneficiary_last_name,
          },
        }
      : {
          entityType: null,
        }),
  };
}

export function parseBeneficiaryPutModel(data: BeneficiaryPutModel): BeneficiaryPutSchema {
  return {
    name: data.nickname,
    "payment_types[]": data.paymentTypes,
    bank_account_holder_name: data.bank.account.holderName,
    currency: data.bank.account.currencyCode,
    account_number: data.bank.account.number,
    bic_swift: data.bank.account.bic,
    iban: data.bank.account.iban,
    bank_account_type: data.bank.account.type,
    bank_country: data.bank.countryCode,
    bank_address: data.bank.address,
    bank_name: data.bank.name,
    beneficiary_address: data.contact?.address === null ? " " : data.contact?.address,
    beneficiary_city: data.contact?.city === null ? " " : data.contact?.city,
    beneficiary_country: data.contact?.countryCode,
    beneficiary_entity_type: data.entityType,
    beneficiary_external_reference: data.contact?.externalReference,
    beneficiary_identification_type: data.identification?.type,
    beneficiary_identification_value: data.identification?.value,
    beneficiary_postcode: data.contact?.postalCode === null ? " " : data.contact?.postalCode,
    beneficiary_state_or_province:
      data.contact?.stateOrProvince === null ? " " : data.contact?.stateOrProvince,
    email: data.contact?.email,
    on_behalf_of: data.onBehalfOf,
    default_beneficiary: data.default !== undefined ? `${data.default}` : undefined,
    ...(typeof data.bank.account.sortCode === "string"
      ? {
          routing_code_type_1: "sort_code",
          routing_code_value_1: data.bank.account.sortCode,
        }
      : data.bank.account.sortCode === null
      ? {
          routing_code_type_1: null,
          routing_code_value_1: null,
        }
      : undefined),
    ...(data.entityType === "company"
      ? {
          beneficiary_company_name: data.company?.name,
          beneficiary_date_of_birth: data.company?.registrationDate?.toLocaleDateString("sv-SE"),
        }
      : data.entityType === "individual"
      ? {
          beneficiary_first_name: data.individual?.firstName,
          beneficiary_last_name: data.individual?.lastName,
          beneficiary_date_of_birth: data.individual?.birthDate?.toLocaleDateString("sv-SE"),
        }
      : undefined),
  };
}

export function updateBeneficiaryModel(
  data: BeneficiaryModel,
  update: RecursivePartial<BeneficiaryPutModel>,
): BeneficiaryPutModel {
  const entityType = thisOrThat(update.entityType, data.entityType);
  const updateCompany = update.entityType === "company" ? update.company : undefined;
  const updateIndividual = update.entityType === "individual" ? update.individual : undefined;
  const company = data.entityType === "company" ? data.company : undefined;
  const individual = data.entityType === "individual" ? data.individual : undefined;

  return {
    bank: {
      account: {
        currencyCode: update.bank?.account?.currencyCode ?? data.bank.account.currencyCode,
        holderName: update.bank?.account?.holderName ?? data.bank.account.holderName,
        bic: thisOrThat(update.bank?.account?.bic, data.bank.account.bic),
        iban: thisOrThat(update.bank?.account?.iban, data.bank.account.iban),
        number: thisOrThat(update.bank?.account?.number, data.bank.account.number),
        sortCode: thisOrThat(update.bank?.account?.sortCode, data.bank.account.sortCode),
        type: thisOrThat(update.bank?.account?.type, data.bank.account.type),
      },
      countryCode: update.bank?.countryCode ?? data.bank.countryCode,
      address: thisOrThat(update.bank?.address, data.bank.address.join(", ")),
      name: thisOrThat(update.bank?.name, data.bank.name),
    },
    contact: {
      address: thisOrThat(update.contact?.address, data.contact.address.join(", ")),
      city: thisOrThat(update.contact?.city, data.contact.city),
      countryCode: thisOrThat(update.contact?.countryCode, data.contact.countryCode),
      email: thisOrThat(update.contact?.email, data.contact.email),
      externalReference: thisOrThat(
        update.contact?.externalReference,
        data.contact.externalReference,
      ),
      postalCode: thisOrThat(update.contact?.postalCode, data.contact.postalCode),
      stateOrProvince: thisOrThat(update.contact?.stateOrProvince, data.contact.stateOrProvince),
    },
    nickname: update.nickname ?? data.nickname,
    default: update.default !== undefined ? update.default : data.default,
    identification: {
      type: thisOrThat(update.identification?.type, data.identification.type),
      value: thisOrThat(update.identification?.value, data.identification.value),
    },
    paymentTypes: update.paymentTypes ?? data.paymentTypes,
    ...(entityType === "company"
      ? {
          entityType,
          company: {
            name: thisOrThat(updateCompany?.name, company?.name),
            registrationDate: thisOrThat(
              updateCompany?.registrationDate,
              company?.registrationDate,
            ),
          },
        }
      : entityType === "individual"
      ? {
          entityType,
          individual: {
            birthDate: thisOrThat(updateIndividual?.birthDate, individual?.birthDate),
            firstName: thisOrThat(updateIndividual?.firstName, individual?.firstName),
            lastName: thisOrThat(updateIndividual?.lastName, individual?.lastName),
          },
        }
      : {
          entityType,
        }),
  };
}

export function parseFindCriteriaModel(data: FindCriteriaModel): FindCriteriaSchema {
  const beneficiaryDateOfBirth =
    data.entityType === "company"
      ? data.company?.registrationDate
      : data.entityType === "individual"
      ? data.individual?.birthDate
      : undefined;

  return {
    "routing_code_type[0]": data.bank?.account?.sortCode ? "sort_code" : undefined,
    "routing_code_value[0]": data.bank?.account?.sortCode,
    account_number: data.bank?.account?.number,
    bank_account_holder_name: data.bank?.account?.holderName,
    bank_account_type: data.bank?.account?.type,
    bank_name: data.bank?.name,
    beneficiary_city: data.contact?.city,
    beneficiary_company_name: data.entityType === "company" ? data.company?.name : undefined,
    beneficiary_country: data.contact?.countryCode,
    beneficiary_date_of_birth: beneficiaryDateOfBirth?.toLocaleDateString("sv-SE"),
    beneficiary_entity_type: data.entityType,
    beneficiary_external_reference: data.contact?.externalReference,
    beneficiary_first_name:
      data.entityType === "individual" ? data.individual?.firstName : undefined,
    beneficiary_last_name: data.entityType === "individual" ? data.individual?.lastName : undefined,
    beneficiary_postcode: data.contact?.postalCode,
    beneficiary_state_or_province: data.contact?.stateOrProvince,
    bic_swift: data.bank?.account?.bic,
    currency: data.bank?.account?.currencyCode,
    default_beneficiary:
      data.defaultBeneficiary !== undefined ? `${data.defaultBeneficiary}` : undefined,
    iban: data.bank?.account?.iban,
    name: data.nickname,
    on_behalf_of: data.onBehalfOf,
    order: data.order ? orderFieldMapping[data.order] : undefined,
    order_asc_desc: data.orderDirection,
    page: (data.offset ?? 0) + 1,
    per_page: data.limit ?? 20,
    scope: data.scope,
  };
}

export function parseRequirementsSchema(data: RequirementsSchema): RequirementsModel {
  return {
    paymentType: data.payment_type,
    bank: {
      account: {
        bic: !!data.bic_swift,
        iban: !!data.iban,
        number: !!data.acct_number,
        sortCode: !!data.sort_code,
      },
    },
    contact: {
      address: !!data.beneficiary_address,
      city: !!data.beneficiary_city,
      countryCode: !!data.beneficiary_country,
      postalCode: !!data.beneficiary_postcode,
      stateOrProvince: !!data.beneficiary_state_or_province,
    },
    ...(data.beneficiary_entity_type === "company"
      ? {
          entityType: "company",
          company: {
            name: !!data.beneficiary_company_name,
            registrationDate: !!data.beneficiary_company_name,
          },
        }
      : {
          entityType: "individual",
          individual: {
            birthDate: !!(data.beneficiary_first_name || data.beneficiary_last_name),
            firstName: !!data.beneficiary_first_name,
            lastName: !!data.beneficiary_last_name,
          },
        }),
  };
}

export function parseGetRequirementsModel(data: GetRequirementsModel): GetRequirementsSchema {
  return {
    bank_account_country: data.bank.account.countryCode,
    beneficiary_country: data.contact?.countryCode,
    currency: data.bank.account.currencyCode,
  };
}
