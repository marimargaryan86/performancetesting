import { redirect } from "@sveltejs/kit";
import routeConfig from "routeConfig";
import { getCookie, type BookingSessionSearch } from "../../booking-flow";

export function load(event): {
  bookingSession: BookingSessionSearch;
} {
  try {
    return {
      bookingSession: getCookie("search", event),
    };
  } catch (err) {
    throw redirect(303, routeConfig.routes.tripManagement.routes.book.root);
  }
}
