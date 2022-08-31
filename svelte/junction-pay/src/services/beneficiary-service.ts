import utils from "$lib/utils";
import type { BeneficiaryData } from "$models/beneficiary-models/models";
import config from "../config";
import BaseService from "./base-service";

export default class BeneficiaryService extends BaseService {
  async create(data: BeneficiaryData): Promise<void> {
    // TODO: Error handling.

    try {
      await fetch(new URL("/beneficiaries/create", config.CC_API_BASE_URL), {
        method: "POST",
        body: JSON.stringify({
          identity: {
            bank_account_holder_name: data.accountHolderName,
            ...(data.type === "company"
              ? {
                  beneficiary_company_name: data.companyName,
                }
              : {
                  beneficiary_first_name: data.individualFirstName,
                  beneficiary_last_name: data.individualLastName,
                  bank_account_holder_name: data.accountHolderName,
                }),
          },
          name: data.nickname,
          bank_country: data.accountCountry.name,
          currency: data.accountCurrency.code,
          beneficiary_entity_type: data.type,
          beneficiary_date_of_birth:
            data.type === "company"
              ? utils.formatDate(data.companyRegistrationDate)
              : utils.formatDate(data.individualBirthDate),
          beneficiary_address: data.addressLine,
          beneficiary_postcode: data.addressPostalCode,
          beneficiary_country: data.addressCountry.name,
          account_number: data.accountNumber,
          routing_code_type_1: data.paymentOptions.includes("sort-code") ? "sort_code" : undefined,
          routing_code_value_1: data.sortCode.replace(/-/g, ""),
          bic_swift: data.bicSwift,
          iban: data.iban,
        }),
        headers: {
          "Content-Type": "application/json",
          "X-Auth-Token": await this.getApiKey(),
        },
      });
    } catch (err) {
      //
    }
  }

  async find(page = 1): Promise<unknown> {
    const response = await fetch(
      utils.buildUrl(new URL("beneficiaries/find", config.CC_API_BASE_URL), { page }),
      {
        method: "GET",
        headers: {
          "X-Auth-Token": await this.getApiKey(),
        },
      },
    );

    return await response.json();
  }
}
