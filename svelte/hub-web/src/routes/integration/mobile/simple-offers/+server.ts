import integrationInstancesServer from "~/integration-instances";
import { server } from "./simple-offer-service";

export const POST = server({
  create({ locals: { session } }, { data }) {
    return integrationInstancesServer.junctionMobileApi.simpleOfferSearches.create({
      session,
      data,
    });
  },
  findOffers({ locals: { session } }, { id }) {
    return integrationInstancesServer.junctionMobileApi.simpleOfferSearches.findOffers({
      session,
      simpleOfferSearchId: id,
    });
  },
  get({ locals: { session } }, { id }) {
    return integrationInstancesServer.junctionMobileApi.simpleOfferSearches.get({ session, id });
  },
});
