import { bookingSessionModel, type BookingSessionModel } from "./trip-management";
import type { RequestEvent } from "@sveltejs/kit";
import { cookieStore } from "stores/cookie-store.server";

function setBookingSession(
  bookingSession: BookingSessionModel,
  event: RequestEvent,
): BookingSessionModel {
  cookieStore.searchToken.set(bookingSession, event);

  return bookingSession;
}

function getBookingSession(event: RequestEvent): BookingSessionModel {
  try {
    return bookingSessionModel.parse(cookieStore.searchToken.get(event));
  } catch {
    cookieStore.searchToken.delete(event);

    throw new Error("Failed to decode booking session");
  }
}

export default {
  setBookingSession,
  getBookingSession,
};
