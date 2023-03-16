import type { DateRange } from "models/date-time";
import type { TransactionStatus } from "models/transaction";
import { writable, type Writable } from "svelte/store";

interface ReturnType {
  searchQuery: Writable<string>;
  dateRange: Writable<DateRange | undefined>;
  status: Writable<TransactionStatus[]>;
}

export function load(): ReturnType {
  return {
    searchQuery: writable(""),
    dateRange: writable(),
    status: writable([]),
  };
}
