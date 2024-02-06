import integrationInstances from "~/integration-instances";
import accountService from "./account-service";
import { serverServiceFactory } from "../../framework";

const factory = serverServiceFactory(accountService);

export const POST = factory({
  find({ locals: { session } }, { cursor, limit }) {
    return integrationInstances.junctionHubApi.accounts.find({ session, cursor, limit });
  },
  get({ locals: { session } }, { id }) {
    return integrationInstances.junctionHubApi.accounts.get({ session, id });
  },
});
