import type { BookingModel } from "models/booking";
import { parseBooking } from "../parsers/booking";
import type { GetBookingResponseSchema } from "../schemas/booking";
import JunctionClientApiService from "./junction-client-api-service";

export default class BookingService extends JunctionClientApiService {
  async getBooking(id: string): Promise<BookingModel> {
    const resp = await this.makeRequest(`/bookings/${id}`, {
      queryParams: {
        include: [
          "order",
          "order.journey",
          "details",
          "details.cabinClass",
          "details.legType",
        ].join(","),
      },
    });

    if (resp.status !== 200) {
      throw new Error(`Junction Pay error: ${resp.status}`);
    }

    const data = (await resp.json()) as GetBookingResponseSchema;

    return parseBooking(data.data, data.included);
  }
}
