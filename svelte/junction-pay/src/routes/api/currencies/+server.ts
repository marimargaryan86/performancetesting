import type { OrderField } from "$integration/currency-cloud/models/currencies";
import type { RequestEvent } from "@sveltejs/kit";
import { jsonResponse } from "../helpers";
import instances from "../instances";
import { parseFindCriteriaSchema } from "../parsers/currencies";
import type { FindCriteriaSchema } from "../schemas/currencies";
import { validateFindCriteriaSchema } from "../validators/currencies";

export async function GET(request: RequestEvent): Promise<Response> {
  try {
    const query = request.url.searchParams;

    const criteria: FindCriteriaSchema = {
      "order[asc]": (query.get("order[asc]") as OrderField) ?? undefined,
      "order[desc]": (query.get("order[desc]") as OrderField) ?? undefined,
      "page[limit]": parseInt(query.get("page[limit]") ?? "20", 10) ?? undefined,
      "page[offset]": parseInt(query.get("page[offset]") ?? "0", 10) ?? undefined,
    };

    return jsonResponse(
      await instances.currencyService.find(
        parseFindCriteriaSchema(validateFindCriteriaSchema(criteria)),
      ),
    );
  } catch (error) {
    return jsonResponse({ message: "Unprocessable entity", detail: error }, 422);
  }
}
