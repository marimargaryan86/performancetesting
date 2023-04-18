import integrationInstances from "integration-instances";
import type { AccountModel } from "models/account";
import { getToken } from "utils/auth";
import type { LayoutServerLoadEvent } from "./$types";

interface BreadCrumb {
  url: string;
  label: string;
}

function getBreadCrumbs(event: LayoutServerLoadEvent): BreadCrumb[] {
  const baseUrl = "/pay/accounts";

  const breadCrumbs = [
    { url: baseUrl, label: "Accounts" },
    { url: `${baseUrl}/${event.params.accountId}`, label: "Balances" },
  ];

  if (event.params.currencyCode) {
    breadCrumbs.push({
      url: `${baseUrl}/${event.params.accountId}/${event.params.currencyCode}`,
      label: `Transactions (${event.params.currencyCode.toUpperCase()})`,
    });
  }

  return breadCrumbs;
}

export async function load(event: LayoutServerLoadEvent): Promise<{
  breadCrumbs: BreadCrumb[];
  account: AccountModel;
}> {
  return {
    breadCrumbs: getBreadCrumbs(event),
    account: await integrationInstances.junctionPay.accounts.getAccount(
      getToken(event),
      event.params.accountId,
    ),
  };
}
