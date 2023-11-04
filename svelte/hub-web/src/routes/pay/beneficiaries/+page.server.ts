import integrationInstances from "integration-instances";
import type { Beneficiary } from "integration/junction-hub-api/schemas/beneficiary";
import type { PaginatedData } from "models/common";
import { getSession } from "utils/auth";

export function load(event): {
  beneficiaries: Promise<PaginatedData<Beneficiary>>;
} {
  return {
    beneficiaries: integrationInstances.junctionHubApi.beneficiaries.listBeneficiaries({
      session: getSession(event),
    }),
  };
}

export const actions = {
  async listBeneficiaries(event): Promise<{ beneficiaries: PaginatedData<Beneficiary> } | void> {
    const formData = await event.request.formData();
    const cursor = formData.get("cursor")?.toString();

    if (!cursor) {
      return;
    }

    return {
      beneficiaries: await integrationInstances.junctionHubApi.beneficiaries.listBeneficiaries({
        session: getSession(event),
        cursor,
      }),
    };
  },
};
