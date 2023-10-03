import integrationInstances from "integration-instances";
import type { ConversionModel } from "integration/junction-hub-api/schemas/conversion";
import type { PaginatedData } from "models/common";
import { getSession } from "utils/auth";

export function load(event): {
  conversions: Promise<PaginatedData<ConversionModel>>;
} {
  return {
    conversions: integrationInstances.junctionHubApi.conversions.listConversions({
      session: getSession(event),
    }),
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
      conversions: await integrationInstances.junctionHubApi.conversions.listConversions({
        session: getSession(event),
        cursor,
      }),
    };
  },
};
