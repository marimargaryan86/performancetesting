export function yymmdd(date: Date): string {
  return date.toLocaleDateString("en-GB", {
    year: "2-digit",
    month: "2-digit",
    day: "2-digit",
  });
}

export function monthName(
  date: Date,
  options: Intl.DateTimeFormatOptions["month"] = "long",
): string {
  return date.toLocaleDateString("en-GB", { month: options });
}
