import integrationInstances from "integration-instances";
import { serverServiceFactory } from "../../framework";
import balanceService from "./balance-service";

const factory = serverServiceFactory(balanceService);

export const POST = factory({
  create({ locals: { session } }, { accountId, data }) {
    return integrationInstances.junctionHubApi.balances.create({ session, accountId, data });
  },
  find({ locals: { session } }, { accountId, cursor, limit }) {
    return integrationInstances.junctionHubApi.balances.find({ session, accountId, cursor, limit });
  },
});
