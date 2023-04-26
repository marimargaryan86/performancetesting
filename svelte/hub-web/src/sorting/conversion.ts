import type { ConversionModel } from "models/conversion";
import type { DirectionY } from "models/spatial";
import type { FlattenedObject } from "utils/common";

/* eslint-disable max-lines-per-function */
export function sortConversions(
  conversions: ConversionModel[],
  options: { by: FlattenedObject<ConversionModel>; direction: DirectionY },
): ConversionModel[] {
  const nextConversions = [...conversions];

  /* eslint-disable complexity */
  nextConversions.sort((a, b) => {
    switch (options.by) {
      case "transaction.reference":
        return 0 - ((a.transaction?.reference ?? 0) < (b.transaction?.reference ?? 0) ? 1 : -1);
      case "createdAt":
        return 0 - (a.createdAt > b.createdAt ? 1 : -1);
      case "settledAt":
        return 0 - (a.settledAt > b.settledAt ? 1 : -1);
      case "sellAmount.currency":
        return 0 - ((a.sellAmount.currency ?? 0) < (b.sellAmount.currency ?? 0) ? 1 : -1);
      case "buyAmount.currency":
        return 0 - ((a.buyAmount.currency ?? 0) < (b.buyAmount.currency ?? 0) ? 1 : -1);
      case "transaction.rates.fxQuote":
        return (
          0 - ((a.transaction?.rates.fxQuote ?? 0) < (b.transaction?.rates.fxQuote ?? 0) ? 1 : -1)
        );
      case "executedRate":
        return 0 - (a.executedRate < b.executedRate ? 1 : -1);
      case "fxDelta":
        return 0 - ((a.fxDelta ?? 0) < (b.fxDelta ?? 0) ? 1 : -1);
      case "transaction.rates.fxBuffer":
        return (
          0 - ((a.transaction?.rates.fxBuffer ?? 0) < (b.transaction?.rates.fxBuffer ?? 0) ? 1 : -1)
        );
      case "fxStatus":
        return 0 - ((a.fxStatus ?? 0) < (b.fxStatus ?? 0) ? 1 : -1);
      default:
        return 0;
    }
  });
  /* eslint-enable-complexity */

  if (options.direction === "up") {
    return nextConversions.reverse();
  }

  return nextConversions;
}
/* eslint-enable max-lines-per-function */
