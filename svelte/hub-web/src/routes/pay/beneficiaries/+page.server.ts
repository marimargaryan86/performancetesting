import integrationInstances from "integration-instances";
import type { BeneficiaryModel } from "models/beneficiary";
import type { PaginatedData } from "models/common";
import { getToken } from "utils/auth";

export function load(event): {
  beneficiaries: Promise<PaginatedData<BeneficiaryModel>>;
} {
  return {
    beneficiaries: integrationInstances.junctionPayApi.beneficiaries.listBeneficiaries(
      getToken(event),
    ),
  };
}

export const actions = {
  async listBeneficiaries(
    event,
  ): Promise<{ beneficiaries: PaginatedData<BeneficiaryModel> } | void> {
    const formData = await event.request.formData();
    const cursor = formData.get("cursor")?.toString();

    if (!cursor) {
      return;
    }

    return {
      beneficiaries: await integrationInstances.junctionPayApi.beneficiaries.listBeneficiaries(
        getToken(event),
        cursor,
      ),
    };
  },
};
