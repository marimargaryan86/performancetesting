import integrationInstances from "integration-instances";
import type { PaginatedData } from "models/common";
import type { ConversionModel } from "models/conversion";
import { getToken } from "utils/auth";

export function load(event): {
  conversions: Promise<PaginatedData<ConversionModel>>;
} {
  return {
    conversions: integrationInstances.junctionPay.conversions.listConversions(getToken(event)),
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
      conversions: await integrationInstances.junctionPay.conversions.listConversions(
        getToken(event),
        cursor,
      ),
    };
  },
};
