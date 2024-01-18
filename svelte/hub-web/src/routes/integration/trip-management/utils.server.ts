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

function offersEqual(
  offerA: BookingSessionModel["selected"],
  offerB: BookingSessionModel["selected"],
): boolean {
  return Boolean(
    offerA &&
      offerB &&
      offerA.offerId === offerB.offerId &&
      JSON.stringify(offerA.optionIds) === JSON.stringify(offerB.optionIds),
  );
}

export default {
  offersEqual,
  setBookingSession,
  getBookingSession,
};
