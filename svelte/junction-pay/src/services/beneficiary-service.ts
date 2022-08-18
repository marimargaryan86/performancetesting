import { wizardStore } from "$lib/stores";
import utils from "$lib/utils";
import type {
  AddBeneficiaryBankDetailsCombined,
  AddBeneficiaryBankDetailsCompany,
  AddBeneficiaryBankDetailsIndividual,
  AddBeneficiaryDetailsData,
  BeneficiaryWizardComplete,
} from "$models/beneficiary-models";
import type { ValidationError } from "$models/common-models";
import BaseService from "./base-service";

export default class BeneficiaryService extends BaseService {
  private validateAddBeneficiaryDetailsData(
    data: Partial<AddBeneficiaryDetailsData>,
  ): [boolean, ValidationError<AddBeneficiaryDetailsData>] {
    const errors: ValidationError<AddBeneficiaryDetailsData> = {
      nickname: !data.nickname?.trim().length ? ["Nickname is missing"] : undefined,
      beneficiaryCountry: !data.beneficiaryCountry ? ["Beneficiary country is missing"] : undefined,
      bankAccountCountry: !data.bankAccountCountry
        ? ["Bank account country is missing"]
        : undefined,
    };

    return [this.containsNoErrors(errors), errors];
  }

  private validateAddIndividualBankDetails(
    data: Partial<AddBeneficiaryBankDetailsCombined>,
  ): [boolean, ValidationError<AddBeneficiaryBankDetailsCombined>] {
    if (data.beneficiaryEntityType === "individual") {
      const errors: ValidationError<AddBeneficiaryBankDetailsIndividual> = {
        beneficiaryEntityType: !data.beneficiaryEntityType?.trim().length
          ? ["Missing Entity Type"]
          : undefined,
        beneficiaryFirstName: !data.beneficiaryFirstName?.trim().length
          ? ["Missing First Name"]
          : undefined,
        beneficiaryLastName: !data.beneficiaryLastName?.trim().length
          ? ["Missing Last Name"]
          : undefined,
        beneficiaryDateOfBirth: !data.beneficiaryDateOfBirth
          ? ["Missing Date of Birth"]
          : undefined,
        options: !data.options ? ["Missing options"] : undefined,
        paymentTypes: !data.paymentTypes ? ["Missing Payment Types"] : undefined,
        accountName: !data.accountName?.trim().length ? ["Missing account name"] : undefined,
        addressLine:
          (data.paymentTypes?.length ?? 0) > 0 && !data.addressLine?.trim().length
            ? ["Missing address"]
            : undefined,
        postCode:
          (data.paymentTypes?.length ?? 0) > 0 && !data.postCode?.trim().length
            ? ["Missing postal code"]
            : undefined,
        sortCode:
          data.options?.includes("sort_code") && !data.sortCode?.trim().length
            ? ["Missing sort code"]
            : undefined,
        accountNumber:
          data.options?.includes("sort_code") && !data.accountNumber
            ? ["Missing account number"]
            : undefined,
        bic: data.options?.includes("swift") && !data.bic ? ["Missing BIC/Swift code"] : undefined,
        iban: data.options?.includes("swift") && !data.iban ? ["Missing IBAN"] : undefined,
      };

      return [this.containsNoErrors(errors), errors];
    }
    return [
      true,
      {
        bic: ["Error with type"],
      },
    ];
  }

  private validateAddCompanyBankDetails(
    data: Partial<AddBeneficiaryBankDetailsCombined>,
  ): [boolean, ValidationError<AddBeneficiaryBankDetailsCombined>] {
    if (data.beneficiaryEntityType === "company") {
      const errors: ValidationError<AddBeneficiaryBankDetailsCompany> = {
        beneficiaryEntityType: !data.beneficiaryEntityType?.trim().length
          ? ["Missing Entity Type"]
          : undefined,

        beneficiaryEntityName: !data.beneficiaryEntityName?.trim().length
          ? ["Missing Entity name"]
          : undefined,

        beneficiaryDateOfBirth: !data.beneficiaryDateOfBirth
          ? ["Missing Date of Birth"]
          : undefined,
        accountName: !data.accountName?.trim().length ? ["Missing account name"] : undefined,
        paymentTypes:
          data.paymentTypes && data.paymentTypes.length < 1 ? ["Missing Payment Types"] : undefined,
        addressLine:
          (data.paymentTypes?.length ?? 0) > 0 && !data.addressLine?.trim().length
            ? ["Missing address"]
            : undefined,
        postCode:
          (data.paymentTypes?.length ?? 0) > 0 && !data.postCode?.trim().length
            ? ["Missing postal code"]
            : undefined,
        options: data.options && data.options.length < 1 ? ["Missing options"] : undefined,
        sortCode:
          data.options?.includes("sort_code") && !data.sortCode?.trim().length
            ? ["Missing sort code"]
            : undefined,
        accountNumber:
          data.options?.includes("account_number") && !data.accountNumber
            ? ["Missing account number"]
            : undefined,
        bic: data.options?.includes("swift") && !data.bic ? ["Missing BIC/Swift code"] : undefined,
        iban: data.options?.includes("swift") && !data.iban ? ["Missing IBAN"] : undefined,
      };
      return [this.containsNoErrors(errors), errors];
    }
    return [
      true,
      {
        bic: ["Error with type"],
      },
    ];
  }

  async createBeneficary(data: Partial<BeneficiaryWizardComplete>): Promise<void> {
    const { auth_token } = await this.loginAndReturnApiKey();
    const response = await fetch("https://devapi.currencycloud.com/v2/beneficiaries/create", {
      method: "POST",
      body: JSON.stringify(utils.mapStoreToBeneficiaryApi(data)),
      headers: {
        "Content-Type": "application/json",
        "X-Auth-Token": auth_token,
      },
    });
    // add log out
    return response.json();
  }

  async addBeneficiaryDetails(data: Partial<AddBeneficiaryDetailsData>): Promise<void> {
    const [valid, errors] = this.validateAddBeneficiaryDetailsData(data);

    if (!valid) {
      throw errors;
    }

    wizardStore.addDetails(data);

    await utils.sleep(1500);

    if (data.nickname === "asd") {
      throw new Error("An unexpected error occured");
    }
  }

  async addBeneficiaryBankDetails(data: Partial<AddBeneficiaryBankDetailsCombined>): Promise<void> {
    const [valid, errors] =
      data.beneficiaryEntityType === "company"
        ? this.validateAddCompanyBankDetails(data)
        : this.validateAddIndividualBankDetails(data);

    if (!valid) {
      throw errors;
    }

    wizardStore.addDetails(data);
    await utils.sleep(1500);
  }

  async fetchBeneficiarys(page = 1) {
    const { auth_token } = await this.loginAndReturnApiKey();

    const response = await fetch(
      `https://devapi.currencycloud.com/v2/beneficiaries/find?page=${page}`,
      {
        method: "GET",
        headers: {
          "X-Auth-Token": auth_token,
        },
      },
    );

    return await response.json();
  }
}
