import { redirect } from "@sveltejs/kit";
import integrationInstances from "~/integration-instances";
import routeConfig from "$lib/route-config";
import type * as HubSchemas from "~/integration/junction-hub-api/schemas";
import {
  getCookie,
  type BookingSessionSelect,
} from "$lib/components/pages/trip-management/booking-flow-train/booking-flow";

export async function load(event): Promise<{
  bookingSession: BookingSessionSelect;
  profile: HubSchemas.UserProfile;
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
