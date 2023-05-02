import type { CurrencyModel, MoneyModel } from "models/money";

export function formatAmountAndCode(amount: MoneyModel, currencies: CurrencyModel[] = []): string {
  return `${formatAmount(amount, currencies)} ${amount.currency.toUpperCase()}`;
}

export function formatAmount(amount: MoneyModel, currencies: CurrencyModel[] = []): string {
  const currency = currencies.find((item) => item.code === amount.currency);
  let finalAmount = amount.amount;

  if (currency) {
    finalAmount /= 10 ** currency.minorUnits;
  }

  return finalAmount.toLocaleString("en-GB", { minimumFractionDigits: 2 });
}
