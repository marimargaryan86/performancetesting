import { redirect } from "@sveltejs/kit";
import routeConfig from "$lib/route-config";
import { getCookie, type BookingSessionSearch } from "$lib/booking-manager/booking-manager";

export function load(event): {
  bookingSession: BookingSessionSearch;
} {
  try {
    return {
      bookingSession: getCookie("search", event),
    };
  } catch (err) {
    throw redirect(
      303,
      routeConfig.routes.tripManagement.routes.book.routes[event.params.searchType].root,
    );
  }
}
