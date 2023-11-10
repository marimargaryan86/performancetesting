import type { PriceBreakdownType, Price } from "integration/common/schemas/price";

export function formatAmountAndCode(amount: Price): string {
  return `${formatAmount(amount)} ${amount.currency.toUpperCase()}`;
}

export function formatAmount(money: Price, sign = false): string {
  return money.amount.toLocaleString("en-US", {
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
