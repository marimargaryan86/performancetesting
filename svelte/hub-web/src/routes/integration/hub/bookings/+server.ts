import integrationInstances from "~/integration-instances";
import { serverServiceFactory } from "../../framework";
import bookingService from "./booking-service";

const factory = serverServiceFactory(bookingService);

export const POST = factory({
  get({ locals: { session } }, { id }) {
    return integrationInstances.junctionHubApi.bookings.get({ session, id });
  },
});
