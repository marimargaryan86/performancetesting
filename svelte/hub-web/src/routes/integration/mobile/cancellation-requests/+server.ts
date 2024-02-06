import integrationInstances from "~/integration-instances";
import { serverServiceFactory } from "../../framework";
import cancellationRequestService from "./cancellation-request-service";

const factory = serverServiceFactory(cancellationRequestService);

export const POST = factory({
  create({ locals: { session } }, { data }) {
    return integrationInstances.junctionMobileApi.cancellations.create({ session, data });
  },
  get({ locals: { session } }, { id }) {
    return integrationInstances.junctionMobileApi.cancellations.get({ session, id });
  },
});
