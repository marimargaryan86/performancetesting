import type { RecursivePartial } from "$integration/currency-cloud/models/common";
import type {
  BankAccountType,
  EntityType,
  ScopeType,
} from "$integration/currency-cloud/schemas/beneficiaries";
import type { RequestEvent } from "@sveltejs/kit";
import { jsonRequest, jsonResponse } from "../helpers";
import instances from "../instances";
import { parseCreateBeneficiarySchema, parseFindCriteriaSchema } from "../parsers/beneficiaries";
import type { CreateBeneficiarySchema, FindCriteriaSchema } from "../schemas/beneficiaries";
import { validateCreateBeneficiarySchema } from "../validators/beneficiaries/create";
import { validateFindCriteriaSchema } from "../validators/beneficiaries/find";
import type { OrderField } from "$integration/currency-cloud/models/beneficiaries/find";

export async function POST(request: RequestEvent): Promise<Response> {
  let reqJsonData: RecursivePartial<CreateBeneficiarySchema>;

  try {
    reqJsonData = await jsonRequest(request);
  } catch (error) {
    return jsonResponse({ message: "Bad request", detail: error }, 400);
  }

  try {
    const reqData = parseCreateBeneficiarySchema(validateCreateBeneficiarySchema(reqJsonData));

    return jsonResponse(await instances.beneficiaryService.create(reqData));
  } catch (error) {
    return jsonResponse({ message: "Unprocessable entity", detail: error }, 422);
  }
}

export async function GET(request: RequestEvent): Promise<Response> {
  const query = request.url.searchParams;
  const reqQueryData: RecursivePartial<FindCriteriaSchema> = {
    "orderBy[asc]": (query.get("orderBy[asc]") as OrderField) ?? undefined,
    "orderBy[desc]": (query.get("orderBy[desc]") as OrderField) ?? undefined,
    "page[limit]": parseInt(query.get("page[limit]") ?? "20", 10) ?? undefined,
    "page[offset]": parseInt(query.get("page[offset]") ?? "0", 10) ?? undefined,
    bankAccountBic: query.get("bankAccountBic") ?? undefined,
    bankAccountCurrencyCode: query.get("bankAccountCurrencyCode") ?? undefined,
    bankAccountHolderName: query.get("bankAccountHolderName") ?? undefined,
    bankAccountIban: query.get("bankAccountIban") ?? undefined,
    bankAccountNumber: query.get("bankAccountNumber") ?? undefined,
    bankAccountSortCode: query.get("bankAccountSortCode") ?? undefined,
    bankAccountType: (query.get("bankAccountType") as BankAccountType) ?? undefined,
    bankName: query.get("bankName") ?? undefined,
    companyName: query.get("companyName") ?? undefined,
    companyRegistrationDate: query.get("companyRegistrationDate") ?? undefined,
    contactCity: query.get("contactCity") ?? undefined,
    contactCountryCode: query.get("contactCountryCode") ?? undefined,
    contactExternalReference: query.get("contactExternalReference") ?? undefined,
    contactPostalCode: query.get("contactPostalCode") ?? undefined,
    contactStateOrProvince: query.get("contactStateOrProvince") ?? undefined,
    defaultBeneficiary: query.get("defaultBeneficiary")
      ? query.get("defaultBeneficiary") === "true"
      : undefined,
    entityType: (query.get("entityType") as EntityType) ?? undefined,
    individualBirthDate: query.get("individualBirthDate") ?? undefined,
    individualFirstName: query.get("individualFirstName") ?? undefined,
    individualLastName: query.get("individualLastName") ?? undefined,
    nickname: query.get("nickname") ?? undefined,
    scope: (query.get("scope") as ScopeType) ?? undefined,
  };

  try {
    const reqData = parseFindCriteriaSchema(validateFindCriteriaSchema(reqQueryData));

    return jsonResponse(await instances.beneficiaryService.find(reqData));
  } catch (error) {
    if (typeof error === "object") {
      return jsonResponse({ message: "Unprocessable entity", detail: error }, 422);
    }

    return jsonResponse({ message: "Internal server error" }, 500);
  }
}
