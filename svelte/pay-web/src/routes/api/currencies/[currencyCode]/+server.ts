import { validateCurrencyCode } from "$integration/currency-cloud/validators/common";
import type { RequestEvent } from "@sveltejs/kit";
import { jsonResponse } from "../../helpers";
import instances from "../../instances";

export async function GET(request: RequestEvent<{ currencyCode: string }>): Promise<Response> {
  try {
    const error = validateCurrencyCode(request.params.currencyCode);

    if (error) {
      throw error;
    }

    return jsonResponse(await instances.currencyService.get(request.params.currencyCode));
  } catch (error) {
    if (error === "NOT_FOUND") {
      return jsonResponse({ message: "Not found" }, 404);
    }

    return jsonResponse({ message: "Unprocessable entity", detail: error }, 422);
  }
}
