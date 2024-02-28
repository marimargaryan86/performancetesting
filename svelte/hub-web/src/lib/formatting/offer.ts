import type { Translator } from "$lib/i18n";
import type { OfferSortOption } from "$lib/sorting/offer";

export function formatOfferSortOption(t: Translator, option?: OfferSortOption): string | undefined {
  if (!option) {
    return undefined;
  }

  return t(`sortOptions.${option}`);
}
