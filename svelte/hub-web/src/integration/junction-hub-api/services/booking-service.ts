import type { SessionModel } from "models/user";
import { parseBooking } from "../parsers/booking";
import type { BookingIncludes, BookingModel, BookingSchema } from "../schemas/booking";
import JunctionHubApiService from "./junction-hub-api-service";

export default class BookingService extends JunctionHubApiService {
  async getBooking({ session, id }: { session: SessionModel; id: string }): Promise<BookingModel> {
    const resp = await this.makeRequest<{
      data: BookingSchema;
      included: BookingIncludes[];
    }>(`/bookings/${id}`, {
      queryParams: {
        include: [
          "order",
          "order.journey",
          "details",
          "details.cabinClass",
          "details.legType",
        ].join(","),
      },
      session,
    });

    return parseBooking(resp.json.data, resp.json.included);
  }
}
