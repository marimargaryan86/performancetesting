import { orderFieldMapping, type AccountModel, type FindCriteriaModel } from "../models/accounts";
import type { AccountSchema, FindCriteriaSchema } from "../schemas/accounts";

export function parseAccountSchema(data: AccountSchema): AccountModel {
  return {
    id: data.id,
    createdAt: new Date(data.created_at),
    modifiedAt: new Date(data.updated_at),
    name: data.account_name,
    entityType: data.legal_entity_type,
    brand: data.brand,
    contact: {
      address: data.street,
      city: data.city,
      countryCode: data.country,
      postalCode: data.postal_code,
      stateOrProvince: data.state_or_province,
    },
    identification:
      data.identification_type && data.identification_value
        ? {
            type: data.identification_type,
            value: data.identification_value,
          }
        : null,
    agentOrReliance: data.agent_or_reliance,
    apiTrading: data.api_trading,
    bankAccountVerificationStatus: data.bank_account_verified,
    onlineTrading: data.online_trading,
    phoneTrading: data.phone_trading,
    processThirdPartyFunds: data.process_third_party_funds,
    ref: data.your_reference,
    settlementType: data.settlement_type,
    shortRef: data.short_reference,
    spreadTable: data.spread_table,
    status: data.status,
    termsAndConditionsAccepted: data.terms_and_conditions_accepted,
  };
}

export function parseFindCriteriaModel(data: FindCriteriaModel): FindCriteriaSchema {
  return {
    account_name: data.name,
    bank_account_verified: data.bankAccountVerificationStatus,
    brand: data.brand,
    city: data.contact?.city,
    country: data.contact?.countryCode,
    page: (data.offset ?? 0) + 1,
    per_page: data.limit === undefined ? 20 : data.limit,
    postal_code: data.contact?.postalCode,
    spread_table: data.spreadTable,
    state_or_province: data.contact?.stateOrProvince,
    status: data.status,
    street: data.contact?.address,
    your_reference: data.ref,
    order_asc_desc: data.orderDirection,
    order: data.order ? orderFieldMapping[data.order] : undefined,
  };
}
