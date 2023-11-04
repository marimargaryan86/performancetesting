import type { Currency } from "integration/junction-hub-api/schemas/currency";
import type { PriceBreakdownType, Price } from "integration/common/schemas/price";

export function formatAmountAndCode(
  amount: Price,
  currencies: Map<string, Currency> = new Map(),
): string {
  return `${formatAmount(amount, currencies)} ${amount.currency.toUpperCase()}`;
}

export function formatAmount(
  money: Price,
  currencies: Map<string, Currency> = new Map(),
  sign = false,
): string {
  const currency = currencies.get(money.currency);
  let finalAmount = money.amount;

  if (currency) {
    finalAmount /= 10 ** currency.minorUnits;
  }

  return finalAmount.toLocaleString("en-US", {
    minimumFractionDigits: 2,
    style: sign ? "currency" : undefined,
    currency: sign ? money.currency : undefined,
  });
}

export function formatPriceBreakdownType(type: PriceBreakdownType): string {
  if (type === "base-fare") {
    return "Base fare";
  } else if (type === "company-mark-up") {
    return "Company mark-up";
  } else if (type === "reseller-mark-up") {
    return "Reseller mark-up";
  } else if (type === "service-mark-up") {
    return "Service mark-up";
  } else if (type === "tax") {
    return "Taxes";
  }

  throw new Error(`Unknown price breakdown type ${type}`);
}
