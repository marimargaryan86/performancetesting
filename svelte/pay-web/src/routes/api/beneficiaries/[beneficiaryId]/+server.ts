import { BeneficiaryServiceError } from "$integration/currency-cloud/services/beneficiary-service";
import type { RecursivePartial } from "$integration/currency-cloud/models/common";
import type { RequestEvent } from "@sveltejs/kit";
import { jsonRequest, jsonResponse } from "../../helpers";
import instances from "../../instances";
import { parseUpdateBeneficiarySchema } from "../../parsers/beneficiaries";
import type { CreateBeneficiarySchema } from "../../schemas/beneficiaries";
import { validateUpdateBeneficiarySchema } from "../../validators/beneficiaries/update";

export async function GET(request: RequestEvent<{ beneficiaryId: string }>): Promise<Response> {
  try {
    return jsonResponse(await instances.beneficiaryService.get(request.params.beneficiaryId));
  } catch (error) {
    const validationError = error instanceof Array ? error : undefined;

    if (validationError) {
      return jsonResponse({ message: "Bad request", detail: error }, 400);
    }

    const errorEnum = error as BeneficiaryServiceError;

    switch (errorEnum) {
      case BeneficiaryServiceError.NOT_FOUND:
        return jsonResponse({ message: "Not found" }, 404);
      default:
        return jsonResponse({ message: "Internal server error" }, 500);
    }
  }
}

export async function DELETE(request: RequestEvent<{ beneficiaryId: string }>): Promise<Response> {
  try {
    return jsonResponse(
      await instances.beneficiaryService.remove(request.params.beneficiaryId),
      204,
    );
  } catch (error) {
    const validationError = error instanceof Array ? error : undefined;

    if (validationError) {
      return jsonResponse({ message: "Bad request", detail: error }, 400);
    }

    const errorEnum = error as BeneficiaryServiceError;

    switch (errorEnum) {
      case BeneficiaryServiceError.NOT_FOUND:
        return jsonResponse({ message: "Not found" }, 404);
      default:
        return jsonResponse({ message: "Internal server error" }, 500);
    }
  }
}

export async function PATCH(request: RequestEvent<{ beneficiaryId: string }>): Promise<Response> {
  let reqJsonData: RecursivePartial<CreateBeneficiarySchema>;

  try {
    reqJsonData = await jsonRequest(request);
  } catch (error) {
    return jsonResponse({ message: "Bad request", detail: error }, 400);
  }

  try {
    return jsonResponse(
      await instances.beneficiaryService.update(
        request.params.beneficiaryId,
        parseUpdateBeneficiarySchema(validateUpdateBeneficiarySchema(reqJsonData)),
      ),
    );
  } catch (error) {
    const badRequestError = error instanceof Array ? error : undefined;

    if (badRequestError) {
      return jsonResponse({ message: "Bad request", detail: error }, 400);
    }

    const validationError = typeof error === "object" ? error : undefined;

    if (validationError) {
      return jsonResponse({ message: "Unprocessable entity", detail: error }, 422);
    }

    const errorEnum = error as BeneficiaryServiceError;

    switch (errorEnum) {
      case BeneficiaryServiceError.NOT_FOUND:
        return jsonResponse({ message: "Not found" }, 404);
      default:
        return jsonResponse({ message: "Internal server error" }, 500);
    }
  }
}
