import { getSession } from "utils/auth";
import * as devalue from "devalue";
import type { RequestEvent } from "./$types";
import { type ActionFailure, fail, error } from "@sveltejs/kit";
import { z } from "zod";
import integrationInstances from "integration-instances";
import type { Beneficiary, BeneficiaryPut } from "integration/junction-hub-api/schemas/beneficiary";
import type { Account } from "integration/junction-hub-api/schemas/account";

function getBeneficiaryData(event: RequestEvent): BeneficiaryPut | undefined {
  const cookieData = event.cookies.get("beneficiary-data");

  return cookieData
    ? devalue.parse(decodeURIComponent(Buffer.from(cookieData, "base64").toString()))
    : undefined;
}

export async function load(event): Promise<{
  beneficiary: BeneficiaryPut;
  accounts: Promise<Account[]>;
}> {
  const session = getSession(event);
  const accounts = integrationInstances.junctionHubApi.accounts
    .listAccounts({ session })
    .then((data) => data.data);

  let beneficiary = getBeneficiaryData(event);

  if (event.params.slug === "add") {
    if (beneficiary?.id) {
      beneficiary = undefined;
      event.cookies.delete("beneficiary-data", { path: "/", httpOnly: false, secure: false });
    }
  } else if (beneficiary?.id !== event.params.slug) {
    beneficiary = await integrationInstances.junctionHubApi.beneficiaries.getBeneficiary({
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

export const actions = {
  async default(
    event,
  ): Promise<
    | { beneficiary: Beneficiary }
    | ActionFailure<{ validation?: z.ZodFormattedError<Beneficiary>; service?: string }>
  > {
    const beneficiary = getBeneficiaryData(event);

    if (!beneficiary) {
      return fail(422);
    }

    try {
      if (beneficiary.id) {
        return {
          beneficiary: await integrationInstances.junctionHubApi.beneficiaries.updateBeneficiary({
            session: getSession(event),
            id: beneficiary.id,
            data: beneficiary,
          }),
        };
      }

      return {
        beneficiary: await integrationInstances.junctionHubApi.beneficiaries.createBeneficiary({
          session: getSession(event),
          data: beneficiary,
        }),
      };
    } catch (err) {
      if (err instanceof z.ZodError) {
        return fail(422, { validation: err.format() });
      }

      if (err instanceof Error) {
        return fail(400, { service: err.message });
      }
    }

    return fail(500);
  },
};
