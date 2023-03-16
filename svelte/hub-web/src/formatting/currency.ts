import type { CurrencyAmount } from "models/currency";

export function amountAndCode(amount: CurrencyAmount): string {
  const formattedAmount = Intl.NumberFormat("en-GB").format(amount.amount);

  return `${formattedAmount} ${amount.code.toUpperCase()}`;
}
