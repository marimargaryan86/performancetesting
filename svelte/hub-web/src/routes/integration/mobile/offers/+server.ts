import integrationInstances from "~/integration-instances";
import { server } from "./offer-service";

export const POST = server({
  create({ locals: { session } }, { data }) {
    return integrationInstances.junctionMobileApi.offers.create({ session, data });
  },
  get({ locals: { session } }, { id }) {
    return integrationInstances.junctionMobileApi.offers.get({ session, id });
  },
});
