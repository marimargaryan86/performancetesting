import type { TransactionModel } from "models/transaction";
import { parseTransaction } from "../parsers/transaction";
import type { ListTransactionsResponseSchema } from "../schemas/transaction";
import type CompanyService from "./company-service";
import JunctionPayService from "./junction-pay-service";
import type { CompanyModel } from "models/company";
import type { PaginatedData } from "models/common";

export default class TransactionService extends JunctionPayService {
  private readonly companyService: CompanyService;

  constructor(baseUrl: string, companyService: CompanyService) {
    super(baseUrl);

    this.companyService = companyService;
  }

  private getCompanies(
    data: ListTransactionsResponseSchema,
    token: string,
  ): Promise<CompanyModel[]> {
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

    return Promise.all(companyRequests);
  }

  async listTransactions(token: string, cursor?: string): Promise<PaginatedData<TransactionModel>> {
    const resp = await this.makeRequest("/transactions", {
      token,
      queryParams: { "page[cursor]": cursor },
    });

    if (resp.status !== 200) {
      throw new Error(`Junction Pay error: ${resp.status}`);
    }

    const data = (await resp.json()) as ListTransactionsResponseSchema;
    const companies = await this.getCompanies(data, token);

    return {
      data: data.data.map((item) => parseTransaction(item, companies)),
      cursor: TransactionService.getCursor(data),
    };
  }
}
