import * as devalue from "devalue";
import type { RequestEvent } from "./$types";
import { error } from "@sveltejs/kit";
import integrationInstances from "~/integration-instances";
import type * as HubSchemas from "~/integration/junction-hub-api/schemas";

function getBeneficiaryData(event: RequestEvent): HubSchemas.BeneficiaryPut | undefined {
  const cookieData = event.cookies.get("beneficiary-data");

  return cookieData
    ? devalue.parse(decodeURIComponent(Buffer.from(cookieData, "base64").toString()))
    : undefined;
}

export async function load(event): Promise<{
  beneficiary: HubSchemas.BeneficiaryPut;
  accounts: Promise<HubSchemas.Account[]>;
}> {
  const session = event.locals.session;
  const accounts = integrationInstances.junctionHubApi.accounts
    .find({ session })
    .then((data) => data.data);

  let beneficiary = getBeneficiaryData(event);

  if (event.params.slug === "add") {
    if (beneficiary?.id) {
      beneficiary = undefined;
      event.cookies.delete("beneficiary-data", { path: "/", httpOnly: false, secure: false });
    }
  } else if (beneficiary?.id !== event.params.slug) {
    beneficiary = await integrationInstances.junctionHubApi.beneficiaries.get({
      session,
      id: event.params.slug,
    });
    event.cookies.delete("beneficiary-data", { path: "/", httpOnly: false, secure: false });
  }

  if (!beneficiary) {
    throw error(404, { message: "Beneficiary not found" });
  }

  return { beneficiary, accounts };
}
