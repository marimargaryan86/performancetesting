import integrationInstances from "integration-instances";
import type { Beneficiary } from "integration/junction-hub-api/schemas/beneficiary";
import type { PaginatedData } from "models/common";
import { getSession } from "utils/auth";

const LIST_BENEFICIARIES_LIMIT = 20;

export function load(event): {
  beneficiaries: Promise<PaginatedData<Beneficiary>>;
} {
  return {
    beneficiaries: integrationInstances.junctionHubApi.beneficiaries.listBeneficiaries({
      session: getSession(event),
      limit: LIST_BENEFICIARIES_LIMIT,
    }),
  };
}

export const actions = {
  async listBeneficiaries(event): Promise<{ beneficiaries: PaginatedData<Beneficiary> }> {
    const formData = await event.request.formData();
    const cursor = formData.get("cursor")?.toString();

    if (!cursor) {
      return { beneficiaries: { data: [] } };
    }

    return {
      beneficiaries: await integrationInstances.junctionHubApi.beneficiaries.listBeneficiaries({
        session: getSession(event),
        limit: LIST_BENEFICIARIES_LIMIT,
        cursor,
      }),
    };
  },
};
