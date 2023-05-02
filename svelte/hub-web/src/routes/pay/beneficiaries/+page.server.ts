import integrationInstances from "integration-instances";
import type { BeneficiaryModel } from "models/beneficiary";

export function load(): { beneficiaries: BeneficiaryModel[] } {
  return {
    beneficiaries: integrationInstances.junctionPay.beneficiaries.listBeneficiaries(),
  };
}
