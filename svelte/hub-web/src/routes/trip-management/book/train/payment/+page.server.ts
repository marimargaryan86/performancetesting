import { redirect } from "@sveltejs/kit";
import integrationInstances from "~/integration-instances";
import routeConfig from "~/route-config";
import type { UserProfile } from "~/integration/junction-hub-api/schemas/user";
import { getCookie, type BookingSessionSelect } from "../../../booking-flow";

export async function load(event): Promise<{
  bookingSession: BookingSessionSelect;
  profile: UserProfile;
}> {
  try {
    return {
      bookingSession: getCookie("select", event),
      profile: await integrationInstances.junctionHubApi.users.getProfile({
        session: event.locals.session,
      }),
    };
  } catch {
    throw redirect(303, routeConfig.routes.tripManagement.routes.book.routes.train.root);
  }
}
