import type { BeneficiaryModel } from "models/beneficiary";
import type { BeneficiarySchema } from "../schemas/beneficiaty";

export function parseBeneficiarySchema(beneficiary: BeneficiarySchema): BeneficiaryModel {
  return {
    countryName: beneficiary.attributes.beneficiaryAddress.countryCode,
    currency: {
      code: beneficiary.relationships.currency.data.id,
      name: "TODO: Impl.",
      minorUnits: 2,
    },
    id: beneficiary.id,
    name: beneficiary.attributes.bankAccountHolderName,
    type: beneficiary.attributes.bankDetails.paymentTypes,
  };
}
