import integrationInstances from "~/integration-instances";
import { serverServiceFactory } from "../../framework";
import tripService from "./trip-service";

const factory = serverServiceFactory(tripService);

export const POST = factory({
  create({ locals: { session } }, { data }) {
    return integrationInstances.junctionMobileApi.trips.create({ session, data });
  },
  findOffers({ locals: { session } }, { id, cursor, limit }) {
    return integrationInstances.junctionMobileApi.trips.findOffers({ session, id, cursor, limit });
  },
  getTripCandidateSearch({ locals: { session } }, { id }) {
    return integrationInstances.junctionMobileApi.trips.getTripCandidateSearch({ session, id });
  },
});
