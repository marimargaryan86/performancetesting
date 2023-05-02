import { error } from "@sveltejs/kit";
import integrationInstances from "integration-instances";
import type { BeneficiaryModel } from "models/beneficiary";
import type { PageServerLoadEvent } from "./$types";

export function load(event: PageServerLoadEvent): { beneficiary?: BeneficiaryModel } {
  if (event.params.slug === "add") {
    return {};
  }

  try {
    return {
      beneficiary: integrationInstances.junctionPay.beneficiaries.getBeneficiary(event.params.slug),
    };
  } catch {
    throw error(404, { message: "Not found" });
  }
}
