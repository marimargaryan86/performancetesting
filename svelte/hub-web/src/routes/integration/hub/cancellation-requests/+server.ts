import integrationInstances from "~/integration-instances";
import { server } from "./cancellation-request-service";

export const POST = server({
  create({ locals: { session } }, { data }) {
    return integrationInstances.junctionHubApi.cancellationRequests.create({ session, data });
  },
});
