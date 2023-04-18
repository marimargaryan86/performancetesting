import type { DateRange } from "models/date-time";
import type { ConversionModel } from "models/conversion";
import { getZeroTimeDate } from "utils/date-time";

export function filterConversions(
  transactions: ConversionModel[],
  filters: {
    query: string;
    dateRange?: DateRange;
  },
): ConversionModel[] {
  const { query, dateRange } = filters;
  const lcQuery = query.toLowerCase();

  return transactions.filter((item) => {
    const settledAt = getZeroTimeDate(item.settledAt);

    return (
      (!dateRange || (dateRange.from <= settledAt && settledAt <= dateRange.to)) &&
      item.id.includes(lcQuery)
    );
  });
}
