import { ActionFailure, fail } from "@sveltejs/kit";
import integrationInstances from "integration-instances";
import integrationInstancesServer from "integration-instances-server";
import type { BookingModel } from "models/booking";
import type { PaginatedData } from "models/common";
import type { TransactionModel } from "models/transaction";
import { getToken } from "utils/auth";

export function load(event): {
  transactions: Promise<PaginatedData<TransactionModel>>;
} {
  return {
    transactions: integrationInstances.junctionPay.transactions.listTransactions(getToken(event)),
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
      booking = await integrationInstancesServer.junctionClientApi.bookings.getBooking(bookingId);
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
      transactions: await integrationInstances.junctionPay.transactions.listTransactions(
        getToken(event),
        cursor,
      ),
    };
  },
};
