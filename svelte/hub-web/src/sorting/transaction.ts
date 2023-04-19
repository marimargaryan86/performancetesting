import type { DirectionY } from "models/spatial";
import type { TransactionModel } from "models/transaction";
import type { FlattenedObject } from "utils/common";

/* eslint-disable max-lines-per-function */
export function sortTransactions(
  transactions: TransactionModel[],
  options: { by: FlattenedObject<TransactionModel>; direction: DirectionY },
): TransactionModel[] {
  const nextTransactions = [...transactions];

  /* eslint-disable complexity */
  nextTransactions.sort((a, b) => {
    switch (options.by) {
      case "id":
        return 0 - (a.id < b.id ? 1 : -1);
      case "parentId":
        return 0 - (a.parentId < b.parentId ? 1 : -1);
      case "createdAt":
        return 0 - (a.createdAt < b.createdAt ? 1 : -1);
      case "payer":
        return 0 - ((a.payer?.name ?? 0) < (b.payer?.name ?? 0) ? 1 : -1);
      case "amounts.quotation.amount":
        return 0 - (a.amounts.quotation.amount < b.amounts.quotation.amount ? 1 : -1);
      case "beneficiary":
        return 0 - ((a.beneficiary?.name ?? 0) < (b.beneficiary?.name ?? 0) ? 1 : -1);
      case "amounts.beneficiary.amount":
        return 0 - (a.amounts.beneficiary.amount < b.amounts.beneficiary.amount ? 1 : -1);
      case "amounts.salesMargin.amount":
        return 0 - (a.amounts.salesMargin.amount < b.amounts.salesMargin.amount ? 1 : -1);
      case "reference":
        return 0 - (a.reference < b.reference ? 1 : -1);
      case "status":
        return 0 - (a.status < b.status ? 1 : -1);
      default:
        return 0;
    }
  });
  /* eslint-enable complexity */

  if (options.direction === "up") {
    return nextTransactions.reverse();
  }

  return nextTransactions;
}
/* eslint-enable max-lines-per-function */
