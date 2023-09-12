import { parseTransactionSchema } from "../parsers/transaction";
import type { TransactionModel, TransactionSchema } from "../schemas/transaction";
import type CompanyService from "./company-service";
import JunctionPayService from "./junction-pay-service";
import type { PaginatedData } from "models/common";
import type { CompanyModel } from "../schemas/company";
import { ensureDefined } from "utils/array";

export default class TransactionService extends JunctionPayService {
  private readonly companyService: CompanyService;

  constructor(baseUrl: string | undefined, companyService: CompanyService) {
    super(baseUrl);

    this.companyService = companyService;
  }

  private getCompanies(
    data: { data: TransactionSchema[]; links: { next: string } },
    token: string,
  ): Promise<CompanyModel[]> {
    const companyIds = new Set(
      data.data
        .flatMap((transaction) => transaction.relationships.beneficiary?.data.id)
        .filter(ensureDefined),
    );
    const companyRequests = Array.from(companyIds).map((id) =>
      this.companyService.getCompanyDetails(token, id),
    );

    return Promise.all(companyRequests);
  }

  async listTransactions(
    token: string,
    cursor?: string,
    limit = 100,
  ): Promise<PaginatedData<TransactionModel>> {
    const resp = await this.makeRequest<{ data: TransactionSchema[]; links: { next: string } }>(
      "/transactions",
      {
        token,
        queryParams: {
          "page[cursor]": cursor,
          "page[limit]": limit,
        },
      },
    );

    if (resp.status !== 200) {
      throw new Error(`Junction Pay error: ${resp.status}`);
    }

    const data = await resp.json();
    const included = { companies: await this.getCompanies(data, token) };

    return {
      data: data.data.map((item) => parseTransactionSchema(item, included)),
      cursor: TransactionService.getCursor(data),
    };
  }
}
