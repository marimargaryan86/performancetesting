import { env } from "$env/dynamic/private";
import junctionClientApi from "integration/junction-client-api/services";

export default {
  junctionClientApi: {
    bookings: new junctionClientApi.BookingService(env.CLIENT_API_BASE_URL, env.CLIENT_API_KEY),
  },
};
