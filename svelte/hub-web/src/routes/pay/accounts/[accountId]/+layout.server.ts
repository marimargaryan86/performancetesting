import { error } from "@sveltejs/kit";
import { mockAccounts } from "mock/account";
import type { AccountModel } from "models/account";
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

export function load(event: LayoutServerLoadEvent): {
  breadCrumbs: BreadCrumb[];
  account: AccountModel;
} {
  const account = mockAccounts.find((item) => item.id === event.params.accountId);

  if (!account) {
    throw error(404, "Not Found");
  }

  return {
    breadCrumbs: getBreadCrumbs(event),
    account,
  };
}
