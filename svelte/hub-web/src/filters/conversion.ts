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
    const createdAt = getZeroTimeDate(item.createdAt);

    return (
      (!dateRange || (dateRange.from <= createdAt && createdAt <= dateRange.to)) &&
      (!status?.length || status.includes(item.fxStatus)) &&
      (!item.transaction || item.transaction.reference.includes(lcQuery))
    );
  });
}
