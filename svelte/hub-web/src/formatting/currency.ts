import type { Infer } from "integration/junction-mobile-api/schema-model.server";
import type { priceBreakdownType, priceModel } from "integration/junction-mobile-api/schemas/price";
import type { CurrencyModel } from "models/money";
import type { z } from "zod";

export function formatAmountAndCode(
  amount: Infer<typeof priceModel>,
  currencies: Map<string, CurrencyModel> = new Map(),
): string {
  return `${formatAmount(amount, currencies)} ${amount.currency.toUpperCase()}`;
}

export function formatAmount(
  money: Infer<typeof priceModel>,
  currencies: Map<string, CurrencyModel> = new Map(),
  sign = false,
): string {
  const currency = currencies.get(money.currency);
  let finalAmount = money.amount;

  if (currency) {
    finalAmount /= 10 ** currency.minorUnits;
  }

  return finalAmount.toLocaleString("en-GB", {
    minimumFractionDigits: 2,
    style: sign ? "currency" : undefined,
    currency: sign ? money.currency : undefined,
  });
}

export function formatPriceBreakdownType(type: z.infer<typeof priceBreakdownType>): string {
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
