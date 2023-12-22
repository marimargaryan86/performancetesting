import type { Locale } from "i18n";
import type { Price } from "integration/common/schemas/price";

export function formatAmount(
  money: Price,
  {
    sign = false,
    fractions = 2,
    locale = "en-GB",
  }: {
    sign?: boolean;
    fractions?: number;
    locale?: Locale;
  } = {},
): string {
  return money.amount.toLocaleString(locale, {
    minimumFractionDigits: fractions,
    style: sign ? "currency" : undefined,
    currency: sign ? money.currency : undefined,
  });
}
