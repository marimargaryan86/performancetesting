import integrationInstances from "~/integration-instances";
import type * as UserSchemas from "~/integration/junction-hub-api/schemas";
import type { PaginatedData } from "$lib/models/common";
import { LIST_USERS_LIMIT } from "./+page.svelte";

export async function load(event): Promise<{ users: PaginatedData<UserSchemas.User> }> {
  return {
    users: await integrationInstances.junctionHubApi.users.find({
      limit: LIST_USERS_LIMIT,
      session: event.locals.session,
    }),
  };
}
