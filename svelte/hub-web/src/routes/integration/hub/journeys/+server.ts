import integrationInstances from "~/integration-instances";
import { server } from "./journey-service";

export const POST = server({
  find({ locals: { session } }, { cursor, limit, sort, filter }) {
    return integrationInstances.junctionHubApi.journeys.find({
      session,
      cursor,
      limit,
      sort,
      filter,
    });
  },
});
