import { parseBooking } from "../parsers/booking";
import type { BookingIncludes, BookingModel, BookingSchema } from "../schemas/booking";
import JunctionClientApiService from "./junction-client-api-service";

export default class BookingService extends JunctionClientApiService {
  async getBooking(id: string): Promise<BookingModel> {
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
    });

    return parseBooking(resp.json.data, resp.json.included);
  }
}
