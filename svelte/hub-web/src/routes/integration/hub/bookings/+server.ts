import integrationInstances from "~/integration-instances";
import { server } from "./booking-service";

export const POST = server({
  get({ locals: { session } }, { id }) {
    return integrationInstances.junctionHubApi.bookings.get({ session, id });
  },
});
