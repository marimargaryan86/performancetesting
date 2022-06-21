function formatCurrency(amount: number, code: string): string {
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

function formatDate(date: Date): string {
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
  day = day === -1 ? 7 : day;

  date.setDate(date.getDate() - day);

  return date;
}

async function sleep(timeMs: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, timeMs));
}

export default {
  formatCurrency,
  getCurrencySign,
  formatDate,
  setZeroTime,
  setWeekStart,
  sleep,
};
