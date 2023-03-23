import type { MoneyModel } from "models/money";

export function formatAmountAndCode(amount: MoneyModel): string {
  return `${formatAmount(amount)} ${amount.currency.toUpperCase()}`;
}

export function formatAmount(amount: MoneyModel): string {
  return amount.amount.toLocaleString("en-GB");
}
