import JunctionHubApiService from "./junction-hub-api-service";
import type { PaginatedData } from "models/common";
import type { Session } from "integration/ory/schemas";
import type { Conversion, ConversionSchema } from "../schemas/conversion";
import { parseIncluded, type IncludedSchemas } from "../schemas/included";
import { JunctionError } from "integration/common/junction-error";

export default class ConversionService extends JunctionHubApiService {
  async find({
    session,
    cursor,
    limit = 100,
  }: {
    session: Session;
    cursor?: string;
    limit?: number;
  }): Promise<PaginatedData<Conversion>> {
    const resp = await this.makeRequest<{
      data: ConversionSchema[];
      included?: IncludedSchemas;
      links: { next: string };
    }>("/conversions", {
      queryParams: {
        include: "transactions",
        "page[cursor]": cursor,
        "page[limit]": limit,
      },
      session,
    });

    const parsed = parseIncluded([...(resp.json.included ?? []), ...resp.json.data]);

    return {
      data: parsed.conversions ?? [],
      cursor: ConversionService.getCursor(resp.json),
    };
  }

  async get({ session, id }: { session: Session; id: string }): Promise<Conversion> {
    const resp = await this.makeRequest<{ data: ConversionSchema; included?: IncludedSchemas }>(
      `/conversions/${id}`,
      { session, queryParams: { include: "transactions" } },
    );

    const parsed = parseIncluded([...(resp.json.included ?? []), resp.json.data]);
    const conversion = parsed.conversions?.find((item) => item.id === id);

    if (!conversion) {
      throw new JunctionError({ status: 404, statusText: "Not found" });
    }

    return conversion;
  }
}
