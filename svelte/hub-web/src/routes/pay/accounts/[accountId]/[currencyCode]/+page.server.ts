import { error } from "@sveltejs/kit";
import { mockBalances } from "mock/currency";
import type { CurrencyAmount } from "models/currency";
import type { PageServerLoadEvent } from "./$types";

export function load(event: PageServerLoadEvent): { balance: CurrencyAmount } {
  const balance = mockBalances.find(
    (item) => item.code.toLowerCase() === event.params.currencyCode.toLowerCase(),
  );

  if (!balance) {
    throw error(404, "Not Found");
  }

  return { balance };
}
