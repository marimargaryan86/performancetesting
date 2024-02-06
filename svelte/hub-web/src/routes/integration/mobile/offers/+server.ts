import integrationInstances from "~/integration-instances";
import { serverServiceFactory } from "../../framework";
import offerService from "./offer-service";

const factory = serverServiceFactory(offerService);

export const POST = factory({
  create({ locals: { session } }, { data }) {
    return integrationInstances.junctionMobileApi.offers.create({ session, data });
  },
  get({ locals: { session } }, { id }) {
    return integrationInstances.junctionMobileApi.offers.get({ session, id });
  },
});
