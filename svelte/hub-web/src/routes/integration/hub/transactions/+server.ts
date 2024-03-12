import integrationInstances from "~/integration-instances";
import { server } from "./transaction-service";

export const POST = server({
  find({ locals: { session } }, { cursor, filter, limit, sort }) {
    return integrationInstances.junctionHubApi.transactions.find({
      session,
      limit,
      cursor,
      sort,
      filter,
    });
  },
  get({ locals: { session } }, { id }) {
    return integrationInstances.junctionHubApi.transactions.get({ session, id });
  },
});
