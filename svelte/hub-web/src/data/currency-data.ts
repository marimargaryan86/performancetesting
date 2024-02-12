import type * as HubSchemas from "~/integration/junction-hub-api/schemas";

const list = [
  { code: "AED", name: "UAE Dirham", minorUnits: 2 },
  { code: "AUD", name: "Australian Dollar", minorUnits: 2 },
  { code: "BGN", name: "Bulgarian Lev", minorUnits: 2 },
  { code: "BHD", name: "Bahraini Dinar", minorUnits: 3 },
  { code: "CAD", name: "Canadian Dollar", minorUnits: 2 },
  { code: "CHF", name: "Swiss Franc", minorUnits: 2 },
  { code: "CNY", name: "Yuan Renminbi", minorUnits: 2 },
  { code: "CZK", name: "Czech Koruna", minorUnits: 2 },
  { code: "DKK", name: "Danish Krone", minorUnits: 2 },
  { code: "EUR", name: "Euro", minorUnits: 2 },
  { code: "GBP", name: "Pound Sterling", minorUnits: 2 },
  { code: "HKD", name: "Hong Kong Dollar", minorUnits: 2 },
  { code: "HUF", name: "Forint", minorUnits: 2 },
  { code: "ILS", name: "New Israeli Sheqel", minorUnits: 2 },
  { code: "JPY", name: "Yen", minorUnits: 0 },
  { code: "KES", name: "Kenyan Shilling", minorUnits: 2 },
  { code: "KWD", name: "Kuwaiti Dinar", minorUnits: 3 },
  { code: "NOK", name: "Norwegian Krone", minorUnits: 2 },
  { code: "NZD", name: "New Zealand Dollar", minorUnits: 2 },
  { code: "OMR", name: "Rial Omani", minorUnits: 3 },
  { code: "PLN", name: "Zloty", minorUnits: 2 },
  { code: "QAR", name: "Qatari Rial", minorUnits: 2 },
  { code: "RON", name: "Romanian Leu", minorUnits: 2 },
  { code: "SAR", name: "Saudi Riyal", minorUnits: 2 },
  { code: "SEK", name: "Swedish Krona", minorUnits: 2 },
  { code: "SGD", name: "Singapore Dollar", minorUnits: 2 },
  { code: "THB", name: "Baht", minorUnits: 2 },
  { code: "TRY", name: "Turkish Lira", minorUnits: 2 },
  { code: "UGX", name: "Uganda Shilling", minorUnits: 0 },
  { code: "USD", name: "US Dollar", minorUnits: 2 },
  { code: "ZAR", name: "Rand", minorUnits: 2 },
] as const;

const mapping = Object.fromEntries(list.map((currency) => [currency.code, currency])) as Record<
  string,
  HubSchemas.Currency
>;

export default { list, mapping };
