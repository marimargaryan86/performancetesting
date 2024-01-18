import integrationInstances from "integration-instances";
import { serverServiceFactory } from "../../framework";
import placeService from "./place-service";

const factory = serverServiceFactory(placeService);

export const POST = factory({
  find({ locals: { session } }, query) {
    return query.length < 3
      ? []
      : integrationInstances.junctionMobileApi.places.find({ session, query });
  },
  get({ locals: { session } }, { id }) {
    return integrationInstances.junctionMobileApi.places.get({ session, id });
  },
});
