import type { FindCriteriaModel, OrderField } from "$integration/currency-cloud/models/accounts";
import type {
  AccountStatus,
  AccountVerificationStatus,
} from "$integration/currency-cloud/schemas/accounts";
import type { RequestEvent } from "@sveltejs/kit";
import { jsonResponse } from "../helpers";
import instances from "../instances";
import { parseFindCriteriaSchema } from "../parsers/accounts";

export async function GET(request: RequestEvent): Promise<Response> {
  try {
    const query = request.url.searchParams;
    const criteria: FindCriteriaModel = parseFindCriteriaSchema({
      "orderBy[asc]": (query.get("orderBy[asc]") as OrderField) ?? undefined,
      "orderBy[desc]": (query.get("orderBy[desc]") as OrderField) ?? undefined,
      "page[limit]": parseInt(query.get("page[limit]") ?? "20", 10) ?? undefined,
      "page[offset]": parseInt(query.get("page[offset]") ?? "0", 10) ?? undefined,
      bankAccountVerificationStatus:
        (query.get("bankAccountVerificationStatus") as AccountVerificationStatus) ?? undefined,
      brand: query.get("brand") ?? undefined,
      contactAddress: query.get("contactAddress") ?? undefined,
      contactCity: query.get("contactCity") ?? undefined,
      contactCountryCode: query.get("contactCountryCode") ?? undefined,
      contactPostalCode: query.get("contactPostalCode") ?? undefined,
      contactStateOrProvince: query.get("contactStateOrProvince") ?? undefined,
      name: query.get("name") ?? undefined,
      ref: query.get("ref") ?? undefined,
      spreadTable: query.get("spreadTable") ?? undefined,
      status: (query.get("status") as AccountStatus) ?? undefined,
    });

    return jsonResponse(await instances.accountService.find(criteria));
  } catch (errors) {
    return jsonResponse({ message: "Unprocessable entity", detail: errors });
  }
}
