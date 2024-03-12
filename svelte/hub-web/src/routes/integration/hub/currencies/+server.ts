import integrationInstances from "~/integration-instances";
import { server } from "./currency-service";

export const POST = server({
  find({ locals: { session } }, { cursor, limit }) {
    return integrationInstances.junctionHubApi.currencies.find({ session, cursor, limit });
  },
});
