import type { ConversionModel, ConversionSchema } from "../schemas/conversion";
import JunctionHubApiService from "./junction-hub-api-service";
import { parseConversionSchema } from "../parsers/conversion";
import type { PaginatedData } from "models/common";
import type { TransactionSchema } from "../schemas/transaction";
import { parseIncluded } from "../parsers/included";
import type { SessionModel } from "models/user";

export default class ConversionService extends JunctionHubApiService {
  async listConversions({
    session,
    cursor,
    limit = 100,
  }: {
    session: SessionModel;
    cursor?: string;
    limit?: number;
  }): Promise<PaginatedData<ConversionModel>> {
    const resp = await this.makeRequest<{
      data: ConversionSchema[];
      included?: TransactionSchema[];
      links: { next: string };
    }>("/conversions", {
      queryParams: {
        include: "transactions",
        "page[cursor]": cursor,
        "page[limit]": limit,
      },
      session,
    });

    const included = parseIncluded(resp.json.included ?? []);

    return {
      data: resp.json.data.map((item) => parseConversionSchema(item, included)),
      cursor: ConversionService.getCursor(resp.json),
    };
  }

  async getConversionDetails({
    session,
    id,
  }: {
    session: SessionModel;
    id: string;
  }): Promise<ConversionModel> {
    const resp = await this.makeRequest<{ data: ConversionSchema; included: TransactionSchema[] }>(
      `/conversions/${id}`,
      { session },
    );

    const included = parseIncluded(resp.json.included);

    return parseConversionSchema(resp.json.data, included);
  }
}
