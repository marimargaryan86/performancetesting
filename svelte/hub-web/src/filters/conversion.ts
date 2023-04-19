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
    const executedAt = getZeroTimeDate(item.executedAt);

    return (
      (!dateRange || (dateRange.from <= executedAt && executedAt <= dateRange.to)) &&
      (!item.transaction || item.transaction.reference.includes(lcQuery))
    );
  });
}
