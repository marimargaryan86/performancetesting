import type { ConversionModel } from "models/conversion";
import type { ListConversionsResponseSchema } from "../schemas/conversion";
import JunctionPayService from "./junction-pay-service";

export default class ConversionService extends JunctionPayService {
  async listConversions(token: string): Promise<ConversionModel[]> {
    const resp = await fetch(this.getResourceUrl("/conversions"), {
      headers: this.getHeadersWithAuth(token),
    });

    if (resp.status !== 200) {
      return [
        ...[...Array(50)].map(() => ({
          id: "00000000-0000-0000-0000-000000000000",
          rate: 1.3,
          settledAt: new Date(),
        })),
      ];
    }

    const data = (await resp.json()) as ListConversionsResponseSchema;

    return data.data.map((item) => ({
      id: item.id,
      rate: item.attributes.rate,
      settledAt: new Date(item.attributes.settledAt),
    }));
  }
}
