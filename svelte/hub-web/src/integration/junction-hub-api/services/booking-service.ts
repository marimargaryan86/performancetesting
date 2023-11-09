import type { SessionModel } from "models/user";
import JunctionHubApiService from "./junction-hub-api-service";
import type { TripBooking, TripBookingSchema } from "../schemas/booking";
import { parseIncluded, type IncludedSchemas } from "../schemas/included";
import { JunctionError } from "integration/common/junction-error";

export default class BookingService extends JunctionHubApiService {
  async get({ session, id }: { session: SessionModel; id: string }): Promise<TripBooking> {
    const resp = await this.makeRequest<{
      data: TripBookingSchema;
      included?: IncludedSchemas;
    }>(`/bookings/${id}`, {
      queryParams: {
        include: [
          "order",
          "order.journey",
          "details",
          "bookingCancellation",
          // "refund", TODO: Uncomment
        ].join(","),
      },
      session,
    });

    const parsed = parseIncluded([...(resp.json.included ?? []), resp.json.data]);
    const booking = parsed.tripBookings?.find((item) => item.id === id);

    if (!booking) {
      throw new JunctionError({ status: 404, statusText: "Not found" });
    }

    return booking;
  }
}
