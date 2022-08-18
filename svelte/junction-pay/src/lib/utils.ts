import type { BeneficiaryWizardComplete, CCBeneficiaryModel } from "$models/beneficiary-models";
import type { LocalStorageWithExpiry } from "$models/common-models";
import { writable, type Readable } from "svelte/store";

function formatCurrency(amount: number, code?: string): string {
  try {
    return amount.toLocaleString("en-US", {
      style: "currency",
      currency: code,
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    });
  } catch {
    return amount.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  }
}

function getCurrencySign(code: string): string {
  return (0)
    .toLocaleString("en-US", {
      style: "currency",
      currency: code,
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    })
    .replace(/\d/g, "")
    .trim();
}

function formatDate(date: Date, type = 0): string {
  if (type === 1) {
    return date.toLocaleDateString("en-GB", { day: "numeric", month: "short", year: "numeric" });
  }

  return date.toLocaleDateString("sv-SE", { day: "2-digit", month: "2-digit", year: "numeric" });
}

function setZeroTime(date: Date): Date {
  date.setHours(0);
  date.setMinutes(0);
  date.setSeconds(0);
  date.setMilliseconds(0);

  return date;
}

function setWeekStart(date: Date): Date {
  let day = date.getDay() - 1;
  day = day === -1 ? 6 : day;

  date.setDate(date.getDate() - day);

  return date;
}

function getWeekDay(date: Date): number {
  const day = date.getDay() - 1;

  return day === -1 ? 6 : day;
}

function compareDates(date1: Date, date2: Date): -1 | 0 | 1 {
  if (date1?.getTime() === date2?.getTime()) {
    return 0;
  }

  if (date1 < date2) {
    return -1;
  }

  return 1;
}

async function sleep(timeMs: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, timeMs));
}

function pendableCall<TResponse, TFunc extends (...args: never[]) => Promise<TResponse>>(
  func: TFunc,
  stopOnSuccess = true,
): { pending: Readable<boolean>; func: TFunc } {
  const store = writable(false);

  async function wrappedFunc(...args: never[]): Promise<TResponse> {
    store.set(true);

    try {
      return await func(...args);
    } catch (e: unknown) {
      store.set(false);

      throw e;
    } finally {
      if (stopOnSuccess) {
        store.set(false);
      }
    }
  }

  return {
    pending: store,
    func: wrappedFunc as TFunc,
  };
}

const weekDays = (() => {
  const date = new Date("2021-08-01");

  return [...Array(7)].map(() => {
    date.setDate(date.getDate() + 1);

    return date.toLocaleDateString("en-GB", { weekday: "short" });
  });
})();

const months = (() => {
  const date = new Date("2021-12-01");

  return [...Array(12)].map(() => {
    date.setMonth(date.getMonth() + 1);

    return date.toLocaleDateString("en-GB", { month: "long" });
  });
})();

type ModelList = Record<string, CCBeneficiaryModel[]>;

function groupByFirstLetter(collection: CCBeneficiaryModel[]) {
  return collection
    .sort((a, b) => {
      if (a.bank_account_holder_name > b.bank_account_holder_name) {
        return 1;
      } else if (b.bank_account_holder_name > a.bank_account_holder_name) {
        return -1;
      } else {
        return 0;
      }
    })
    .reduce((acc: ModelList, current) => {
      const alphabet = current.bank_account_holder_name[0];

      if (!acc[alphabet]) {
        // if theres no letter in there already add it to [letter]: object
        acc[alphabet] = [current];
      } else {
        // if there is add it
        acc[alphabet].push(current);
      }
      return acc;
    }, {});
}

function fetchAndCheckLocalStorageWithExpiry(key: string) {
  if (typeof window === undefined) {
    return undefined;
  }

  const itemStr = localStorage.getItem(key);

  if (!itemStr) {
    return undefined;
  }

  const item: LocalStorageWithExpiry = JSON.parse(itemStr);
  const now = new Date();

  if (now > item.expiry) {
    // do a bit of cleanup
    localStorage.removeItem(key);

    return undefined;
  }

  return item.value;
}

function setLocalStorageWithExpiry(key: string, value: string, ttl: number): void {
  if (typeof window === undefined) {
    return undefined;
  }

  const currentTime = new Date().getTime();

  const item: LocalStorageWithExpiry = {
    value,
    expiry: new Date(currentTime + ttl),
  };

  localStorage.setItem(key, JSON.stringify(item));
}

// @mattias Not sure if i should've just typed the params here. Weird feeling i should've done it like this...
function mapStoreToBeneficiaryApi<T extends Partial<BeneficiaryWizardComplete>>(data: T) {
  let identity = {};

  if (data.beneficiaryEntityType === "company") {
    identity = {
      beneficiary_company_name: data.beneficiaryEntityName,
      bank_account_holder_name: data.beneficiaryEntityName,
    };
  } else if (data.beneficiaryEntityType === "individual") {
    identity = {
      beneficiary_first_name: data.beneficiaryFirstName,
      beneficiary_last_name: data.beneficiaryLastName,
      bank_account_holder_name: `${data.beneficiaryFirstName} ${data.beneficiaryLastName}`,
    };
  }
  return {
    name: data.nickname,
    bank_country: data.bankAccountCountry,
    currency: data.currency,
    beneficiary_entity_type: data.beneficiaryEntityType,
    beneficiary_date_of_birth: data.beneficiaryDateOfBirth?.toISOString().split("T")[0],
    beneficiary_address: data.addressLine,
    beneficiary_postcode: "LS6 3EJ",
    beneficiary_country: data.beneficiaryCountry,
    account_number: data.accountNumber,
    routing_code_type_1: data.sortCode && "sort_code", // We only account sort code as our identifer for now.
    routing_code_value_1: data.sortCode?.replace(/-/g, ""),
    bic_swift: data.bic,
    iban: data.iban,
    ...identity,
  };
}

export default {
  formatCurrency,
  getCurrencySign,
  formatDate,
  setZeroTime,
  setWeekStart,
  getWeekDay,
  compareDates,
  sleep,
  pendableCall,
  weekDays,
  months,
  groupByFirstLetter,
  fetchAndCheckLocalStorageWithExpiry,
  setLocalStorageWithExpiry,
  mapStoreToBeneficiaryApi,
};
