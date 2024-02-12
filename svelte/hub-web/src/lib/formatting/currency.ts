import type { Locale } from "$lib/i18n";
import type * as CommonSchemas from "~/integration/common/schemas";

export function formatAmount(
  money: CommonSchemas.Price,
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
