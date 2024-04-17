import integrationInstancesServer from "~/integration-instances";
import { server } from "./reseller-service";

export const POST = server({
  find({ locals: { session } }, { cursor, limit, filter }) {
    return integrationInstancesServer.junctionHubApi.resellers.find({
      session,
      cursor,
      limit,
      filter,
    });
  },
});
