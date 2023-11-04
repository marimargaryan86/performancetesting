import { URLExtended } from "utils/url";
import * as devalue from "devalue";
import type BookingService from "integration/junction-hub-api/services/booking-service";
import { HUB_INTEGRATION_ROOT } from "../common";

const ROOT = `${HUB_INTEGRATION_ROOT}/bookings`;

async function get({ id }: { id: string }): ReturnType<BookingService["get"]> {
  const url = new URLExtended(ROOT, { base: origin, query: { id, action: "get" } });
  const resp = await fetch(url);

  if (resp.status !== 200) {
    throw new Error("Booking not found");
  }

  return devalue.parse(await resp.text());
}

export default {
  get,
};
