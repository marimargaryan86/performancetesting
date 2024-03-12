import integrationInstances from "~/integration-instances";
import { server } from "./account-service";

export const POST = server({
  find({ locals: { session } }, { cursor, limit }) {
    return integrationInstances.junctionHubApi.accounts.find({ session, cursor, limit });
  },
  get({ locals: { session } }, { id }) {
    return integrationInstances.junctionHubApi.accounts.get({ session, id });
  },
});
