import type { BookingDetailsModel, BookingModel } from "models/booking";
import type { BookingDetailsSchema, BookingSchema } from "../schemas/order";

export function parseBookingDetailsSchema(data: BookingDetailsSchema): BookingDetailsModel {
  throw new Error(`Not implemented ${data}`);
}

export function parseBookingSchema(data: BookingSchema): BookingModel {
  throw new Error(`Not implemented ${data}`);
}
