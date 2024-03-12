import integrationInstances from "~/integration-instances";
import { server } from "./conversion-service";

export const POST = server({
  find({ locals: { session } }, { cursor, limit }) {
    return integrationInstances.junctionHubApi.conversions.find({ session, cursor, limit });
  },
  get({ locals: { session } }, { id }) {
    return integrationInstances.junctionHubApi.conversions.get({ session, id });
  },
});
