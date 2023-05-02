import type { BeneficiaryModel } from "models/beneficiary";
import JunctionPayService from "./junction-pay-service";

export default class BeneficiaryService extends JunctionPayService {
  private readonly beneficiaries: BeneficiaryModel[] = [
    ...[
      "Air France",
      "American Airlines",
      "Snowfall",
      "Etihad Airways",
      "United Airlines",
      "Sabre",
    ].map<BeneficiaryModel>((name, idx) => ({
      id: `00000000-0000-0000-0000-00000000000${idx}`,
      countryName: "United Kingdom",
      currency: {
        code: "GBP",
        minorUnits: 2,
        name: "British Pound",
      },
      name,
      type: "priority",
    })),
  ];

  listBeneficiaries(): BeneficiaryModel[] {
    return this.beneficiaries;
  }

  getBeneficiary(id: string): BeneficiaryModel {
    const beneficiary = this.beneficiaries.find((item) => item.id === id);

    if (!beneficiary) {
      throw new Error(`Junction Pay error: 404`);
    }

    return beneficiary;
  }

  removeBeneficiary(id: string): void {
    const idx = this.beneficiaries.findIndex((item) => item.id === id);

    if (idx === -1) {
      return;
    }

    this.beneficiaries.splice(idx, 1);
  }
}
