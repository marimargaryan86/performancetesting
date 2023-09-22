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

  private async getCompanies(
    data: { data: TransactionSchema[]; links: { next: string } },
    token: string,
  ): Promise<CompanyModel[]> {
    const companyIds = new Set(
      data.data
        .flatMap((transaction) => [
          transaction.relationships.beneficiary?.data.id,
          transaction.relationships.payer?.data.id,
        ])
        .filter(ensureDefined),
    );
    const companyRequests = Array.from(companyIds).map((id) =>
      this.companyService
        .getCompanyDetails(token, id)
        .then((item) => item)
        .catch(() => undefined),
    );

    return (await Promise.all(companyRequests)).filter(ensureDefined);
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

    const included = { companies: await this.getCompanies(resp.json, token) };

    return {
      data: resp.json.data.map((item) => parseTransactionSchema(item, included)),
      cursor: TransactionService.getCursor(resp.json),
    };
  }
}
