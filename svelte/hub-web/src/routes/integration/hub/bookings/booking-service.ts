import type BookingService from "~/integration/junction-hub-api/services/booking-service";
import { clientServiceFactory } from "../../framework";
import type { RouteId } from "./$types";

const factory = clientServiceFactory<BookingService, RouteId>("/integration/hub/bookings");

export default factory({
  get: (params: { id: string }) => [params],
});
