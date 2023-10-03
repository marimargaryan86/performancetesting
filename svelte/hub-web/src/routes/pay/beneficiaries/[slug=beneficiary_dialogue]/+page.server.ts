import { getSession } from "utils/auth";
import * as devalue from "devalue";
import type { RequestEvent } from "./$types";
import { ActionFailure, fail } from "@sveltejs/kit";
import { z } from "zod";
import integrationInstances from "integration-instances";
import type { AccountModel } from "integration/junction-hub-api/schemas/account";
import type { BeneficiaryModel } from "integration/junction-hub-api/schemas/beneficiary";
import {
  beneficiaryModel,
  type CreateBeneficiaryModel,
} from "integration/junction-hub-api/schemas/beneficiary.client";

function getBeneficiaryData(event: RequestEvent): CreateBeneficiaryModel | undefined {
  const cookieData = event.cookies.get("beneficiary-data");

  return cookieData
    ? devalue.parse(decodeURIComponent(Buffer.from(cookieData, "base64").toString()))
    : undefined;
}

export async function load(event): Promise<{
  beneficiary: CreateBeneficiaryModel;
  accounts: Promise<AccountModel[]>;
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

  return {
    beneficiary: beneficiary ?? {
      bankDetails: { type: "iban", paymentType: "regular", accountType: "checking" },
    },
    accounts,
  };
}

export const actions = {
  async default(
    event,
  ): Promise<
    | { beneficiary: BeneficiaryModel }
    | ActionFailure<{ validation?: z.ZodFormattedError<BeneficiaryModel>; service?: string }>
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
            beneficiary: beneficiaryModel.parse(beneficiary),
          }),
        };
      }

      return {
        beneficiary: await integrationInstances.junctionHubApi.beneficiaries.createBeneficiary({
          session: getSession(event),
          beneficiary: beneficiaryModel.omit({ id: true }).parse(beneficiary),
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
