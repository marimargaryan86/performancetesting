import { validateUUID } from "$integration/currency-cloud/validators/common";
import type { RequestEvent } from "@sveltejs/kit";
import { jsonResponse } from "../../helpers";
import instances from "../../instances";

export async function GET(request: RequestEvent<{ accountId: string }>): Promise<Response> {
  try {
    const accountId = request.params.accountId;
    const error = validateUUID(accountId);

    if (error) {
      throw error;
    }

    return jsonResponse(await instances.accountService.get(accountId));
  } catch (errors) {
    return jsonResponse({ message: "Unprocessable entity", detail: errors });
  }
}
