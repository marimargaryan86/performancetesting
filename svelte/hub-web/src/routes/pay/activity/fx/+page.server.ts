import integrationInstances from "integration-instances";
import type { ConversionModel } from "integration/junction-pay/schemas/conversion";
import type { PaginatedData } from "models/common";
import { getToken } from "utils/auth";

export function load(event): {
  conversions: Promise<PaginatedData<ConversionModel>>;
} {
  return {
    conversions: integrationInstances.junctionPayApi.conversions.listConversions(getToken(event)),
  };
}

export const actions = {
  async listConversions(event): Promise<{ conversions: PaginatedData<ConversionModel> } | void> {
    const formData = await event.request.formData();
    const cursor = formData.get("cursor")?.toString();

    if (!cursor) {
      return;
    }

    return {
      conversions: await integrationInstances.junctionPayApi.conversions.listConversions(
        getToken(event),
        cursor,
      ),
    };
  },
};
