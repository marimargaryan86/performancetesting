import integrationInstances from "integration-instances";
import type { Conversion } from "integration/junction-hub-api/schemas/conversion";
import type { PaginatedData } from "models/common";
import { getSession } from "utils/auth";

const LIST_CONVERSIONS_LIMIT = 20;

export function load(event): {
  conversions: Promise<PaginatedData<Conversion>>;
} {
  return {
    conversions: integrationInstances.junctionHubApi.conversions.listConversions({
      session: getSession(event),
      limit: LIST_CONVERSIONS_LIMIT,
    }),
  };
}

export const actions = {
  async listConversions(event): Promise<{ conversions: PaginatedData<Conversion> }> {
    const formData = await event.request.formData();
    const cursor = formData.get("cursor")?.toString();

    if (!cursor) {
      return { conversions: { data: [] } };
    }

    return {
      conversions: await integrationInstances.junctionHubApi.conversions.listConversions({
        session: getSession(event),
        limit: LIST_CONVERSIONS_LIMIT,
        cursor,
      }),
    };
  },
};
