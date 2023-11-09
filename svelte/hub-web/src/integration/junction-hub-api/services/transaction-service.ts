import type CompanyService from "./company-service";
import JunctionHubApiService from "./junction-hub-api-service";
import type { PaginatedData } from "models/common";
import { ensureDefined } from "utils/array";
import type { SessionModel } from "models/user";
import {
  transactionParser,
  type Transaction,
  type TransactionSchema,
} from "../schemas/transaction";
import type { Company } from "../schemas/company";
import type { IncludedMapping } from "../schemas/included";

export default class TransactionService extends JunctionHubApiService {
  private readonly companyService: CompanyService;

  constructor(baseUrl: string | undefined, companyService: CompanyService) {
    super(baseUrl);

    this.companyService = companyService;
  }

  private async getCompanies(data: {
    data: TransactionSchema[];
    session: SessionModel;
  }): Promise<Company[]> {
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
        .get({ session: data.session, id })
        .then((item) => item)
        .catch(() => undefined),
    );

    return (await Promise.all(companyRequests)).filter(ensureDefined);
  }

  async find({
    session,
    cursor,
    limit = 100,
    sort,
    filter,
  }: {
    session: SessionModel;
    cursor?: string;
    limit?: number;
    sort?: "createdAt" | "-createdAt";
    filter?: {
      ids?: string[];
      billIds?: string[];
      externalReference?: string;
    };
  }): Promise<PaginatedData<Transaction>> {
    const resp = await this.makeRequest<{ data: TransactionSchema[]; links: { next: string } }>(
      "/transactions",
      {
        session,
        queryParams: {
          sort,
          "filter[ids][eq]": filter?.ids?.join(","),
          "filter[bill.id][eq]": filter?.billIds?.join(","),
          "filter[externalReference][eq]": filter?.externalReference,
          "page[cursor]": cursor,
          "page[limit]": limit,
        },
      },
    );

    const parsed: IncludedMapping = {
      companies: await this.getCompanies({ data: resp.json.data, session }),
    };

    return {
      data: resp.json.data.map((item) => transactionParser.toModel(item, parsed)),
      cursor: TransactionService.getCursor(resp.json),
    };
  }

  async get({ session, id }: { session: SessionModel; id: string }): Promise<Transaction> {
    const resp = await this.makeRequest<{ data: TransactionSchema }>(`/transactions/${id}`, {
      session,
    });

    const parsed: IncludedMapping = {
      companies: await this.getCompanies({ data: [resp.json.data], session }),
    };

    return transactionParser.toModel(resp.json.data, parsed);
  }
}
