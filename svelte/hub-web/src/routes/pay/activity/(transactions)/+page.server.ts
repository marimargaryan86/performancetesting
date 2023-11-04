import { type ActionFailure, fail } from "@sveltejs/kit";
import integrationInstances from "integration-instances";
import type { TripBooking } from "integration/junction-hub-api/schemas/booking";
import type { Transaction } from "integration/junction-hub-api/schemas/transaction";
import type { PaginatedData } from "models/common";
import { getSession } from "utils/auth";

export function load(event): {
  transactions: Promise<PaginatedData<Transaction>>;
} {
  return {
    transactions: integrationInstances.junctionHubApi.transactions.listTransactions({
      session: getSession(event),
    }),
  };
}

export const actions = {
  async getBooking(event): Promise<{ booking: TripBooking | undefined } | ActionFailure> {
    const formData = await event.request.formData();
    const bookingId = formData.get("bookingId")?.toString();

    if (!bookingId) {
      return fail(404);
    }

    let booking: TripBooking | undefined = undefined;

    try {
      booking = await integrationInstances.junctionHubApi.bookings.getBooking({
        session: getSession(event),
        id: bookingId,
      });
    } catch {
      //
    }

    return { booking };
  },
  async listTransactions(event): Promise<{ transactions: PaginatedData<Transaction> } | void> {
    const formData = await event.request.formData();
    const cursor = formData.get("cursor")?.toString();

    if (!cursor) {
      return;
    }

    return {
      transactions: await integrationInstances.junctionHubApi.transactions.listTransactions({
        session: getSession(event),
        cursor,
      }),
    };
  },
};
