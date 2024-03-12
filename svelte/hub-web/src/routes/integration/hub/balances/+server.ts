import integrationInstances from "~/integration-instances";
import { server } from "./balance-service";

export const POST = server({
  create({ locals: { session } }, { accountId, data }) {
    return integrationInstances.junctionHubApi.balances.create({ session, accountId, data });
  },
  find({ locals: { session } }, { accountId, cursor, limit }) {
    return integrationInstances.junctionHubApi.balances.find({ session, accountId, cursor, limit });
  },
});
