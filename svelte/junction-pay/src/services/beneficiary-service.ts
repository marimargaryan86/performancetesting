import utils from "$lib/utils";
import type { AddBeneficiaryDetailsData } from "$models/beneficiary-models";
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
      currency: !data.currency ? ["Currency is missing"] : undefined,
      holderName: !data.holderName?.trim().length ? ["Card holder name is missing"] : undefined,
    };

    return [this.containsNoErrors(errors), errors];
  }

  async addBeneficiaryDetails(data: Partial<AddBeneficiaryDetailsData>): Promise<void> {
    const [valid, errors] = this.validateAddBeneficiaryDetailsData(data);

    if (!valid) {
      throw errors;
    }

    await utils.sleep(1500);

    if (data.nickname === "asd") {
      throw new Error("An unexpected error occured");
    }
  }
}
