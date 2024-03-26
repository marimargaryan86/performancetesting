import integrationInstances from "~/integration-instances";
import type * as HubSchemas from "~/integration/junction-hub-api/schemas";
import * as OrySchemas from "~/integration/ory/schemas";
import type { PaginatedData } from "$lib/models/common";
import { LIST_RESELLERS_LIMIT } from "./+page.svelte";

export async function load(
  event,
): Promise<{ resellers: PaginatedData<HubSchemas.Reseller>; user: OrySchemas.User }> {
  const [resellers, user] = await Promise.all([
    integrationInstances.junctionHubApi.resellers.find({
      limit: LIST_RESELLERS_LIMIT,
      session: event.locals.session,
    }),
    integrationInstances.junctionHubApi.users.get({
      id: event.params.userId,
      session: event.locals.session,
    }),
  ]);

  return {
    resellers,
    user,
  };
}
