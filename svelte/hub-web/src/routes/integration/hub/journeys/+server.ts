import integrationInstances from "~/integration-instances";
import { serverServiceFactory } from "../../framework";
import journeyService from "./journey-service";

const factory = serverServiceFactory(journeyService);

export const POST = factory({
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
