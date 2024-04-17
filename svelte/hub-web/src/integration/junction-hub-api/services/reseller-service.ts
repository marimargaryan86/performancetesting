import type * as OrySchemas from "~/integration/ory/schemas";
import type { PaginatedData } from "$lib/models/common";
import JunctionHubApiService from "./junction-hub-api-service";
import { resellerParser, type Reseller, type ResellerSchema } from "../schemas";

export default class ResellerService extends JunctionHubApiService {
  async find({
    session,
    cursor,
    limit = 20,
    filter,
  }: {
    session: OrySchemas.Session;
    cursor?: string;
    limit?: number;
    filter?: {
      name?: string;
    };
  }): Promise<PaginatedData<Reseller>> {
    const resp = await this.makeRequest<{ data: ResellerSchema[]; links: { next: string } }>(
      "/resellers",
      {
        session,
        queryParams: {
          "page[cursor]": cursor,
          "page[limit]": limit,
          "filter[name][like]": filter?.name,
        },
      },
    );

    return {
      data: resp.json.data.map(resellerParser.toModel),
      cursor: ResellerService.getCursor(resp.json),
    };
  }
}
