import type { CurrencyAmount } from "models/currency";
import { mockBalances } from "mock/currency";

export function load(): { balances: CurrencyAmount[] } {
  return { balances: [...mockBalances] };
}
