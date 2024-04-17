import integrationInstances from "~/integration-instances";
import * as OrySchemas from "~/integration/ory/schemas";

export async function load(event): Promise<{ user: OrySchemas.User }> {
  const user = await integrationInstances.junctionHubApi.users.get({
    id: event.params.userId,
    session: event.locals.session,
  });

  return { user };
}
