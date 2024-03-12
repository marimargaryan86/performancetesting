import integrationInstances from "~/integration-instances";
import { server } from "./place-service";

export const POST = server({
  find({ locals: { session } }, query) {
    return query.length < 3
      ? []
      : integrationInstances.junctionMobileApi.places.find({ session, query });
  },
  get({ locals: { session } }, { id }) {
    return integrationInstances.junctionMobileApi.places.get({ session, id });
  },
});
