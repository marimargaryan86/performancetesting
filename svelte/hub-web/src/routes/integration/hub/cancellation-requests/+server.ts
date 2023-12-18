import integrationInstances from "integration-instances";
import { serverServiceFactory } from "../../framework";
import cancellationRequestService from "./cancellation-request-service";

const factory = serverServiceFactory(cancellationRequestService);

export const POST = factory({
  create({ locals: { session } }, { data }) {
    return integrationInstances.junctionHubApi.cancellationRequests.create({ session, data });
  },
});
