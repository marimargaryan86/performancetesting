import { parseTransactionSchema } from "../parsers/transaction";
import type { TransactionModel, TransactionSchema } from "../schemas/transaction";
import type CompanyService from "./company-service";
import JunctionHubApiService from "./junction-hub-api-service";
import type { PaginatedData } from "models/common";
import type { CompanyModel } from "../schemas/company";
import { ensureDefined } from "utils/array";
import type { SessionModel } from "models/user";

export default class TransactionService extends JunctionHubApiService {
  private readonly companyService: CompanyService;

  constructor(baseUrl: string | undefined, companyService: CompanyService) {
    super(baseUrl);

    this.companyService = companyService;
  }

  private async getCompanies(data: {
    data: TransactionSchema[];
    session: SessionModel;
  }): Promise<CompanyModel[]> {
    const companyIds = new Set(
      data.data
        .flatMap((transaction) => [
          transaction.relationships?.beneficiary?.data.id,
          transaction.relationships?.payer?.data.id,
        ])
        .filter(ensureDefined),
    );
    const companyRequests = Array.from(companyIds).map((id) =>
      this.companyService
        .getCompanyDetails({ session: data.session, id })
        .then((item) => item)
        .catch(() => undefined),
    );

    return (await Promise.all(companyRequests)).filter(ensureDefined);
  }

  async listTransactions({
    session,
    cursor,
    limit = 100,
  }: {
    session: SessionModel;
    cursor?: string;
    limit?: number;
  }): Promise<PaginatedData<TransactionModel>> {
    const resp = await this.makeRequest<{ data: TransactionSchema[]; links: { next: string } }>(
      "/transactions",
      {
        session,
        queryParams: {
          "page[cursor]": cursor,
          "page[limit]": limit,
        },
      },
    );

    const included = { companies: await this.getCompanies({ data: resp.json.data, session }) };

    return {
      data: resp.json.data.map((item) => parseTransactionSchema(item, included)),
      cursor: TransactionService.getCursor(resp.json),
    };
  }
}
