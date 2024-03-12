import integrationInstances from "~/integration-instances";
import { server } from "./bill-service";

export const POST = server({
  find({ locals: { session } }, { cursor, filter, limit }) {
    return integrationInstances.junctionHubApi.bills.find({
      session,
      cursor,
      filter,
      limit,
    });
  },
  get({ locals: { session } }, { id }) {
    return integrationInstances.junctionHubApi.bills.get({ session, id });
  },
  toggleReconciliation({ locals: { session } }, { bill }) {
    return integrationInstances.junctionHubApi.bills.toggleReconciliation({
      session,
      bill,
    });
  },
});
