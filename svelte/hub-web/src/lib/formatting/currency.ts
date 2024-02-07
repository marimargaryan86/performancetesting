import type { Locale } from "~/i18n";
import type { Price } from "~/integration/common/schemas/price";

export function formatAmount(
  money: Price,
  locale: Locale,
  {
    sign = false,
    fractions = 2,
  }: {
    sign?: boolean;
    fractions?: number;
  } = {},
): string {
  return money.amount.toLocaleString(locale, {
    minimumFractionDigits: fractions,
    style: sign ? "currency" : undefined,
    currency: sign ? money.currency : undefined,
  });
}
