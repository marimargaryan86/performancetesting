import { error } from "@sveltejs/kit";
import { mockBalances } from "mock/currency";
import type { MoneyModel } from "models/money";

export function load(): { balance: MoneyModel } {
  const balance = mockBalances[0];

  if (!balance) {
    throw error(404, "Not Found");
  }

  return { balance };
}
