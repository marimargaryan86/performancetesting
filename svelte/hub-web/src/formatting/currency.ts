import type { CurrencyAmount } from "models/currency";

export function formatAmountAndCode(amount: CurrencyAmount): string {
  return `${formatAmount(amount)} ${amount.code.toUpperCase()}`;
}

export function formatAmount(amount: CurrencyAmount): string {
  return amount.amount.toLocaleString("en-GB");
}
