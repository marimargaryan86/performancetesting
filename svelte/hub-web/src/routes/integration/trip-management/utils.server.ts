import * as devalue from "devalue";
import jwt from "jsonwebtoken";
import { dev } from "$app/environment";
import { bookingSessionModel, type BookingSessionModel } from "./trip-management";
import type { RequestEvent } from "@sveltejs/kit";

const SEARCH_TOKEN_COOKIE = "search-token";
const JWT_SECRET = "secret";
const COOKIE_OPTIONS = {
  httpOnly: true,
  path: "/",
  sameSite: "strict",
  secure: !dev,
} as const;

function setBookingSession(
  bookingSession: BookingSessionModel,
  event: RequestEvent,
): BookingSessionModel {
  event.cookies.set(
    SEARCH_TOKEN_COOKIE,
    jwt.sign(devalue.stringify(bookingSession), JWT_SECRET),
    COOKIE_OPTIONS,
  );

  return bookingSession;
}

function getBookingSession(event: RequestEvent): BookingSessionModel {
  try {
    return bookingSessionModel.parse(
      devalue.parse(JSON.stringify(jwt.decode(event.cookies.get(SEARCH_TOKEN_COOKIE) ?? ""))),
    );
  } catch {
    event.cookies.delete(SEARCH_TOKEN_COOKIE, COOKIE_OPTIONS);
    throw new Error("Failed to decode booking session");
  }
}

export default {
  setBookingSession,
  getBookingSession,
};
