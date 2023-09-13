import type { ConversionModel, ConversionSchema } from "../schemas/conversion";
import JunctionPayService from "./junction-pay-service";
import { parseConversionSchema } from "../parsers/conversion";
import type { PaginatedData } from "models/common";
import type { TransactionSchema } from "../schemas/transaction";
import { parseIncluded } from "../parsers/included";

export default class ConversionService extends JunctionPayService {
  async listConversions(
    token: string,
    cursor?: string,
    limit = 100,
  ): Promise<PaginatedData<ConversionModel>> {
    const resp = await this.makeRequest<{
      data: ConversionSchema[];
      included: TransactionSchema[];
      links: { next: string };
    }>("/conversions", {
      queryParams: {
        include: "transactions",
        "page[cursor]": cursor,
        "page[limit]": limit,
      },
      token,
    });

    const included = parseIncluded(resp.json.included);

    return {
      data: resp.json.data.map((item) => parseConversionSchema(item, included)),
      cursor: ConversionService.getCursor(resp.json),
    };
  }

  async getConversionDetails(token: string, conversionId: string): Promise<ConversionModel> {
    const resp = await this.makeRequest<{ data: ConversionSchema; included: TransactionSchema[] }>(
      `/conversions/${conversionId}`,
      { token },
    );

    const included = parseIncluded(resp.json.included);

    return parseConversionSchema(resp.json.data, included);
  }
}
