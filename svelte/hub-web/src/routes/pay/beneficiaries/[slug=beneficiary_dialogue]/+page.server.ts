import { getToken } from "utils/auth";
import * as devalue from "devalue";
import type { RequestEvent } from "./$types";
import { ActionFailure, fail } from "@sveltejs/kit";
import { z } from "zod";
import { formatError, type FormattedError } from "utils/zod";
import integrationInstances from "integration-instances";
import type { AccountModel } from "integration/junction-pay/schemas/account";
import type { BeneficiaryModel } from "integration/junction-pay/schemas/beneficiary";
import {
  beneficiaryModel,
  type CreateBeneficiaryModel,
} from "integration/junction-pay/schemas/beneficiary.client";

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
  const token = getToken(event);
  const accounts = integrationInstances.junctionPayApi.accounts
    .listAccounts(token)
    .then((data) => data.data);

  let beneficiary = getBeneficiaryData(event);

  if (event.params.slug === "add") {
    if (beneficiary?.id) {
      beneficiary = undefined;
      event.cookies.delete("beneficiary-data", { path: "/", httpOnly: false, secure: false });
    }
  } else if (beneficiary?.id !== event.params.slug) {
    beneficiary = await integrationInstances.junctionPayApi.beneficiaries.getBeneficiary(
      token,
      event.params.slug,
    );
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
    | ActionFailure<{ validation?: FormattedError<BeneficiaryModel>; service?: string }>
  > {
    const beneficiary = getBeneficiaryData(event);

    if (!beneficiary) {
      return fail(422);
    }

    try {
      if (beneficiary.id) {
        return {
          beneficiary: await integrationInstances.junctionPayApi.beneficiaries.updateBeneficiary(
            getToken(event),
            beneficiary.id,
            beneficiaryModel.parse(beneficiary),
          ),
        };
      }

      return {
        beneficiary: await integrationInstances.junctionPayApi.beneficiaries.createBeneficiary(
          getToken(event),
          beneficiaryModel.omit({ id: true }).parse(beneficiary),
        ),
      };
    } catch (err) {
      if (err instanceof z.ZodError) {
        return fail(422, { validation: formatError<BeneficiaryModel>(err) });
      }

      if (err instanceof Error) {
        return fail(400, { service: err.message });
      }
    }

    return fail(500);
  },
};
