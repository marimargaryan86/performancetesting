import type { MoneyModel } from "models/money";
import { mockBalances } from "mock/currency";

export function load(): { balances: MoneyModel[] } {
  return { balances: [...mockBalances] };
}
