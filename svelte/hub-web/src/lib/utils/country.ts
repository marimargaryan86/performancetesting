import type { CountryModel } from "$lib/models/location";
import countryData from "~/data/country-data";

export function findCountry(query: string, country?: CountryModel): boolean {
  const queryLower = query.toLowerCase().replaceAll("+", "").trim();

  return Boolean(
    country?.code.toLowerCase().includes(queryLower) ||
      country?.name.toLowerCase().includes(queryLower) ||
      country?.phoneCode.toLowerCase().includes(queryLower),
  );
}

export function getPhoneNumber(phone: string): { country?: CountryModel; number: string } {
  const formattedPhone = phone.replaceAll(/[+\s]/g, "");
  const country = countryData.list.find((item) => formattedPhone.startsWith(item.phoneCode));
  const number = country ? formattedPhone.slice(country.phoneCode.length) : phone;

  return { country, number };
}
