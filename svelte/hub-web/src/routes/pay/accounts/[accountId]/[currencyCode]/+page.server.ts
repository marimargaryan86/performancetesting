import { error } from "@sveltejs/kit";
import { mockBalances } from "mock/currency";
import type { MoneyModel } from "models/money";
import type { PageServerLoadEvent } from "./$types";

export function load(event: PageServerLoadEvent): { balance: MoneyModel } {
  const balance = mockBalances.find(
    (item) => item.currency.toLowerCase() === event.params.currencyCode.toLowerCase(),
  );

  if (!balance) {
    throw error(404, "Not Found");
  }

  return { balance };
}
