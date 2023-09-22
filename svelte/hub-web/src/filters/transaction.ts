import type {
  TransactionModel,
  TransactionStatus,
} from "integration/junction-pay/schemas/transaction";
import type { DateRange } from "models/date-time";
import { getZeroTimeDate } from "utils/date-time";

export function filterTransactions(
  transactions: TransactionModel[],
  filters: {
    query: string;
    status?: TransactionStatus[];
    dateRange?: DateRange;
  },
): TransactionModel[] {
  const { query, status, dateRange } = filters;
  const lcQuery = query.toLowerCase();

  // eslint-disable-next-line complexity
  return transactions.filter((item) => {
    const createdAt = getZeroTimeDate(item.createdAt);

    return (
      (!dateRange || (dateRange.from <= createdAt && createdAt <= dateRange.to)) &&
      (!status?.length || status.includes(item.status)) &&
      (!item.beneficiary ||
        item.beneficiary?.name?.toLowerCase().includes(lcQuery) ||
        !item.payer ||
        item.payer.name?.toLowerCase().includes(lcQuery) ||
        item.bookingId.includes(lcQuery) ||
        item.reference?.toLowerCase().includes(lcQuery))
    );
  });
}
