import type BookingService from "~/integration/junction-hub-api/services/booking-service";
import type { RequestEvent } from "./$types";
import rpcBase from "../../rpc-base";

const { client, server } = rpcBase<BookingService, RequestEvent>("/integration/hub/bookings")({
  get: (params: { id: string }) => [params],
});

export { server };
export default client;
