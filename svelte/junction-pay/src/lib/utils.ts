function formatCurrency(amount: number, code?: string): string {
  if (!code) {
    return amount.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  }

  return amount.toLocaleString("en-US", {
    style: "currency",
    currency: code,
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
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

const weekDays = (() => {
  const date = new Date("2021-08-01");

  return [...Array(7)].map(() => {
    date.setDate(date.getDate() + 1);

    return date.toLocaleDateString("en-GB", { weekday: "short" });
  });
})();

export default {
  formatCurrency,
  getCurrencySign,
  formatDate,
  setZeroTime,
  setWeekStart,
  getWeekDay,
  compareDates,
  sleep,
  weekDays,
};
