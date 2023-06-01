import { error } from "@sveltejs/kit";
import integrationInstances from "integration-instances";
import type { BeneficiaryModel } from "models/beneficiary";
import { getToken } from "utils/auth.js";

export function load(event): { beneficiary?: Promise<BeneficiaryModel> } {
  if (event.params.slug === "add") {
    return {};
  }

  try {
    return {
      beneficiary: integrationInstances.junctionPay.beneficiaries.getBeneficiary(
        getToken(event),
        event.params.slug,
      ),
    };
  } catch {
    throw error(404, { message: "Not found" });
  }
}
