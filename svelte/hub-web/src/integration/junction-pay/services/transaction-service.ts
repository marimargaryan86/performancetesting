import type { TransactionModel } from "models/transaction";
import { parseTransaction } from "../parsers/transaction";
import type { ListTransactionsResponseSchema } from "../schemas/transaction";
import type CompanyService from "./company-service";
import JunctionPayService from "./junction-pay-service";

export default class TransactionService extends JunctionPayService {
  private readonly companyService: CompanyService;

  constructor(baseUrl: string, companyService: CompanyService) {
    super(baseUrl);

    this.companyService = companyService;
  }

  async listTransactions(token: string): Promise<TransactionModel[]> {
    const resp = await this.makeRequest("/transactions", { token });

    if (resp.status !== 200) {
      throw new Error(`Junction Pay error: ${resp.status}`);
    }

    const data = (await resp.json()) as ListTransactionsResponseSchema;
    const companyIds = new Set(
      data.data.reduce<string[]>(
        (prev, curr) => [
          ...prev,
          curr.relationships.beneficiary.data.id,
          curr.relationships.payer.data.id,
        ],
        [],
      ),
    );
    const companyRequests = Array.from(companyIds).map((id) =>
      this.companyService.getCompanyDetails(token, id),
    );
    const companies = await Promise.all(companyRequests);

    return data.data.map((item) => parseTransaction(item, companies));
  }
}
