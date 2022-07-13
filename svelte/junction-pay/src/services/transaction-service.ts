import type { TransactionModel } from "$models/transaction-models";
import { faker } from "@faker-js/faker";
import BaseService from "./base-service";
import type { TransactionsResponse } from "./schemas/transaction-schemas";

export default class TransactionService extends BaseService {
  async findTransactions(limit = 20, offset = 1): Promise<TransactionModel[]> {
    try {
      const response = await fetch(
        this.buildUrl("/transactions", { "page[cursor]": offset, "page[limit]": limit }),
        {
          method: "GET",
        },
      );
      const data: TransactionsResponse = await response.json();

      return data.data.map((item) => ({
        id: item.id,
        amount: item.attributes.amount,
        completedAt: new Date(item.attributes.completedAt),
        createdAt: new Date(item.attributes.createdAt),
        currencyCode: item.relationships.currency.data.id,
        ref: item.attributes.ref,
        status: item.relationships.status.data.id,
        type: item.relationships.transactionType.data.id,
        balance: {
          // TODO: Fetch balance from endpoint.
          code: faker.finance.currencyCode(),
          amount: parseFloat(faker.finance.amount()),
          id: "",
          name: "",
        },
      }));
    } catch {
      throw new Error("An unexpected error occured");
    }
  }
}
