import integrationInstancesServer from "~/integration-instances";
import { serverServiceFactory } from "../../framework";
import simpleOfferService from "./simple-offer-service";

const factory = serverServiceFactory(simpleOfferService);

export const POST = factory({
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
