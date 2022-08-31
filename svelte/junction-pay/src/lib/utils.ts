import type { ValidationError } from "$models/common-models";
import { writable, type Readable } from "svelte/store";

function formatErrors<T>(errors: ValidationError<T>): ValidationError<T> | undefined {
  return Object.values(errors).filter((value) => !!value).length ? errors : undefined;
}

function removeUndefinedValues<T>(obj: T, treatEmptyAsUndefined = true): T | undefined {
  if (obj instanceof Array) {
    const result = obj
      .map((item) => removeUndefinedValues(item, treatEmptyAsUndefined))
      .filter((item) => item !== undefined);

    return !result.length && treatEmptyAsUndefined ? undefined : (result as unknown as T);
  }

  if (typeof obj === "function") {
    return obj;
  }

  if (typeof obj === "object") {
    const result = Object.fromEntries(
      Object.entries(obj)
        .map(([key, value]) => [key, removeUndefinedValues(value, treatEmptyAsUndefined)])
        .filter(([, value]) => value !== undefined),
    );

    return !Object.keys(result).length && treatEmptyAsUndefined
      ? undefined
      : (result as unknown as T);
  }

  return obj;
}

function buildUrl<TValue extends Record<string, { toString: () => string } | undefined>>(
  url: string | URL,
  params?: TValue,
): string {
  const nextUrl = new URL(url);

  if (params) {
    Object.entries(params).forEach(([name, value]) => {
      if (value !== undefined) {
        nextUrl.searchParams.set(name, value instanceof Array ? value.join(",") : value.toString());
      }
    });
  }

  return nextUrl.toString();
}

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

function setZeroTimeUTC(date: Date): Date {
  date.setUTCHours(0);
  date.setUTCMinutes(0);
  date.setUTCSeconds(0);
  date.setUTCMilliseconds(0);

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

export default {
  formatCurrency,
  getCurrencySign,
  formatDate,
  setZeroTime,
  setZeroTimeUTC,
  setWeekStart,
  getWeekDay,
  compareDates,
  sleep,
  pendableCall,
  weekDays,
  months,
  buildUrl,
  formatErrors,
  removeUndefinedValues,
};
