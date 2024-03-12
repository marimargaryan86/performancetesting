import integrationInstances from "~/integration-instances";
import { server } from "./trip-service";

export const POST = server({
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
