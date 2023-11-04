import integrationInstances from "integration-instances";
import type { Journey } from "integration/junction-hub-api/schemas/journey";
import type { PaginatedData } from "models/common";
import { getSession } from "utils/auth";

export function load(event): { journeys: Promise<PaginatedData<Journey>> } {
  return {
    journeys: integrationInstances.junctionHubApi.journeys.find({
      limit: 20,
      session: getSession(event),
    }),
  };
}
