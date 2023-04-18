import type { ConversionModel } from "models/conversion";
import type { DirectionY } from "models/spatial";
import type { FlattenedObject } from "utils/common";

export function sortConversions(
  conversions: ConversionModel[],
  options: { by: FlattenedObject<ConversionModel>; direction: DirectionY },
): ConversionModel[] {
  const nextConversions = [...conversions];

  nextConversions.sort((a, b) => {
    switch (options.by) {
      case "id":
        return 0 - (a.id < b.id ? 1 : -1);
      case "settledAt":
        return 0 - (a.settledAt < b.settledAt ? 1 : -1);
      case "rate":
        return 0 - (a.rate < b.rate ? 1 : -1);
      default:
        return 0;
    }
  });

  if (options.direction === "up") {
    return nextConversions.reverse();
  }

  return nextConversions;
}
