import type { RecursivePartial } from "$integration/currency-cloud/models/common";
import type { EntityType, PaymentType } from "$integration/currency-cloud/schemas/beneficiaries";
import type { RequestEvent } from "@sveltejs/kit";
import { jsonResponse } from "../../helpers";
import instances from "../../instances";
import { parseGetRequirementsSchema } from "../../parsers/beneficiaries";
import type { GetRequirementsSchema } from "../../schemas/beneficiaries";
import { validateGetRequirementsSchema } from "../../validators/beneficiaries/requirements";

export async function GET(request: RequestEvent): Promise<Response> {
  const query = request.url.searchParams;
  const reqQueryData: RecursivePartial<GetRequirementsSchema> = {
    bankAccountCountryCode: query.get("bankAccountCountryCode") ?? undefined,
    bankAccountCurrencyCode: query.get("bankAccountCurrencyCode") ?? undefined,
    contactCountryCode: query.get("contactCountryCode") ?? undefined,
    entityType: (query.get("entityType") as EntityType) ?? undefined,
    paymentTypes: (query.get("paymentTypes")?.split(",") as PaymentType[]) ?? undefined,
  };

  try {
    const reqData = parseGetRequirementsSchema(validateGetRequirementsSchema(reqQueryData));

    return jsonResponse(await instances.beneficiaryService.getRequirements(reqData));
  } catch (error) {
    return jsonResponse({ message: "Invalid data", detail: error }, 422);
  }
}
