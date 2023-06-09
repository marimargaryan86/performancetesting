import integrationInstances from "integration-instances";
import type { CreateBeneficiaryModel } from "models/beneficiary";
import { getToken } from "utils/auth";
import * as devalue from "devalue";

export async function load(event): Promise<{
  beneficiary: CreateBeneficiaryModel;
}> {
  const cookieData = event.cookies.get("beneficiary-data");
  let beneficiary: CreateBeneficiaryModel | undefined = cookieData
    ? devalue.parse(decodeURIComponent(Buffer.from(cookieData, "base64").toString()))
    : undefined;

  if (event.params.slug === "add") {
    if (beneficiary?.id) {
      beneficiary = undefined;
    }
  } else if (beneficiary?.id !== event.params.slug) {
    beneficiary = await integrationInstances.junctionPay.beneficiaries.getBeneficiary(
      getToken(event),
      event.params.slug,
    );
  }

  return {
    beneficiary: beneficiary ?? {},
  };
}
