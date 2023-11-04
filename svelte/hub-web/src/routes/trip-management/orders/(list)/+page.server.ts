import integrationInstances from "integration-instances";
import type { Journey } from "integration/junction-hub-api/schemas/journey";
import type { PaginatedData } from "models/common";
import { getSession } from "utils/auth";

const LIST_JOURNEYS_LIMIT = 20;

export function load(event): { journeys: Promise<PaginatedData<Journey>> } {
  return {
    journeys: integrationInstances.junctionHubApi.journeys.listJourneys({
      limit: LIST_JOURNEYS_LIMIT,
      session: getSession(event),
    }),
  };
}

export const actions = {
  async listJourneys(event): Promise<{ journeys: PaginatedData<Journey> }> {
    const formData = await event.request.formData();
    const cursor = formData.get("cursor")?.toString();

    if (!cursor) {
      return { journeys: { data: [] } };
    }

    return {
      journeys: await integrationInstances.junctionHubApi.journeys.listJourneys({
        session: getSession(event),
        limit: LIST_JOURNEYS_LIMIT,
        cursor,
      }),
    };
  },
};
