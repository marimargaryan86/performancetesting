import type { ConversionModel } from "integration/junction-hub-api/schemas/conversion";
import type { DirectionY } from "models/spatial";
import type { FlattenedObject } from "utils/common";

export function sortConversions(
  conversions: ConversionModel[],
  options: { by: FlattenedObject<ConversionModel>; direction: DirectionY },
): ConversionModel[] {
  const nextConversions = [...conversions];

  // eslint-disable-next-line complexity
  nextConversions.sort((a, b) => {
    switch (options.by) {
      case "transaction.reference":
        return 0 - ((a.transaction?.reference ?? 0) < (b.transaction?.reference ?? 0) ? 1 : -1);
      case "createdAt":
        return a.createdAt && b.createdAt ? 0 - (a.createdAt > b.createdAt ? 1 : -1) : 0;
      case "settledAt":
        return a.settledAt && b.settledAt ? 0 - (a.settledAt > b.settledAt ? 1 : -1) : 0;
      case "sellAmount.currency":
        return a.sellAmount && b.sellAmount
          ? 0 - ((a.sellAmount.currency ?? 0) < (b.sellAmount.currency ?? 0) ? 1 : -1)
          : 0;
      case "buyAmount.currency":
        return 0 - ((a.buyAmount?.currency ?? 0) < (b.buyAmount?.currency ?? 0) ? 1 : -1);
      case "transaction.rates.fxQuote":
        return (
          0 - ((a.transaction?.rates.fxQuote ?? 0) < (b.transaction?.rates.fxQuote ?? 0) ? 1 : -1)
        );
      case "executedRate":
        return 0 - ((a.executedRate ?? 0) < (b.executedRate ?? 0) ? 1 : -1);
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

  if (options.direction === "up") {
    return nextConversions.reverse();
  }

  return nextConversions;
}
