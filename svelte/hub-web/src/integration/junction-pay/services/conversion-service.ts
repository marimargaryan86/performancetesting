import type { ConversionModel } from "models/conversion";
import type {
  GetConversionDetailsResponseSchema,
  ListConversionDetailsResponseSchema,
} from "../schemas/conversion";
import JunctionPayService from "./junction-pay-service";
import { parseConversion } from "../parsers/conversion";
import type { PaginatedData } from "models/common";

export default class ConversionService extends JunctionPayService {
  async listConversions(token: string, cursor?: string): Promise<PaginatedData<ConversionModel>> {
    const resp = await this.makeRequest("/conversions", {
      queryParams: { include: "transactions", "page[cursor]": cursor },
      token,
    });

    if (resp.status !== 200) {
      throw new Error(`Junction Pay error: ${resp.status}`);
    }

    const data = (await resp.json()) as ListConversionDetailsResponseSchema;

    return {
      data: data.data.map((item) => parseConversion(item, data.included)),
      cursor: ConversionService.getCursor(data),
    };
  }

  async getConversionDetails(conversionId: string, token: string): Promise<ConversionModel> {
    const resp = await this.makeRequest(`/conversions/${conversionId}`, { token });

    if (resp.status !== 200) {
      throw new Error(`Junction Pay error: ${resp.status}`);
    }

    const data = (await resp.json()) as GetConversionDetailsResponseSchema;

    return parseConversion(data.data, data.included);
  }
}
