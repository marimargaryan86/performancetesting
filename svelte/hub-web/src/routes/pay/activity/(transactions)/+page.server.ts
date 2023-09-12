import { ActionFailure, fail } from "@sveltejs/kit";
import integrationInstances from "integration-instances";
import type { BookingModel } from "integration/junction-client-api/schemas/booking.js";
import type { TransactionModel } from "integration/junction-pay/schemas/transaction.js";
import type { PaginatedData } from "models/common";
import { getToken } from "utils/auth";

export function load(event): {
  transactions: Promise<PaginatedData<TransactionModel>>;
} {
  return {
    transactions: integrationInstances.junctionPayApi.transactions.listTransactions(
      getToken(event),
    ),
  };
}

export const actions = {
  async getBooking(event): Promise<{ booking: BookingModel | undefined } | ActionFailure> {
    const formData = await event.request.formData();
    const bookingId = formData.get("bookingId")?.toString();

    if (!bookingId) {
      return fail(404);
    }

    let booking: BookingModel | undefined = undefined;

    try {
      booking = await integrationInstances.junctionClientApi.bookings.getBooking(bookingId);
    } catch {
      //
    }

    return { booking };
  },
  async listTransactions(event): Promise<{ transactions: PaginatedData<TransactionModel> } | void> {
    const formData = await event.request.formData();
    const cursor = formData.get("cursor")?.toString();

    if (!cursor) {
      return;
    }

    return {
      transactions: await integrationInstances.junctionPayApi.transactions.listTransactions(
        getToken(event),
        cursor,
      ),
    };
  },
};
