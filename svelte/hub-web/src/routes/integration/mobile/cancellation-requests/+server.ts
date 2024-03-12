import integrationInstances from "~/integration-instances";
import { server } from "./cancellation-request-service";

export const POST = server({
  create({ locals: { session } }, { data }) {
    return integrationInstances.junctionMobileApi.cancellations.create({ session, data });
  },
  get({ locals: { session } }, { id }) {
    return integrationInstances.junctionMobileApi.cancellations.get({ session, id });
  },
});
