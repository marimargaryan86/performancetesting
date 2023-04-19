import type { DateRange } from "models/date-time";
import type { TransactionStatus } from "models/transaction";
import { writable, type Writable } from "svelte/store";
import type { LayoutLoadEvent } from "./$types";
import type { BreadCrumb } from "components/page/bread-crumbs.svelte";

interface ReturnType {
  searchQuery: Writable<string>;
  dateRange: Writable<DateRange | undefined>;
  status: Writable<TransactionStatus[]>;
  breadCrumbs: { url: string; label: string }[];
}

export function load(event: LayoutLoadEvent): ReturnType {
  const breadCrumbs: BreadCrumb[] = [
    {
      url: "/pay/activity",
      label: "Activity",
    },
  ];

  if (event.route.id === "/pay/activity/(transactions)") {
    breadCrumbs.push({
      url: "/pay/activity",
      label: "Transactions",
    });
  } else if (event.route.id === "/pay/activity/fx") {
    breadCrumbs.push({
      url: "/pay/activity/fx",
      label: "FX",
    });
  }

  return {
    searchQuery: writable(""),
    dateRange: writable(),
    status: writable([]),
    breadCrumbs,
  };
}
