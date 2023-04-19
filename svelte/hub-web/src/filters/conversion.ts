import type { DateRange } from "models/date-time";
import type { ConversionModel, ConversionStatus } from "models/conversion";
import { getZeroTimeDate } from "utils/date-time";

export function filterConversions(
  transactions: ConversionModel[],
  filters: {
    query: string;
    status?: ConversionStatus[];
    dateRange?: DateRange;
  },
): ConversionModel[] {
  const { query, status, dateRange } = filters;
  const lcQuery = query.toLowerCase();

  return transactions.filter((item) => {
    const executedAt = getZeroTimeDate(item.executedAt);

    return (
      (!dateRange || (dateRange.from <= executedAt && executedAt <= dateRange.to)) &&
      (!status?.length || status.includes(item.fxStatus)) &&
      (!item.transaction || item.transaction.reference.includes(lcQuery))
    );
  });
}
