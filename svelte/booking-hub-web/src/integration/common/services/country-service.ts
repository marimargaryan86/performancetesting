import type { CountryModel } from "models/location";
import countries from "../data/countries";

export default class CountryService {
  private readonly countries = countries;

  findCountries(): Map<string, CountryModel> {
    const map = new Map<string, CountryModel>();

    this.countries.forEach((c) => map.set(c.code, c));

    return map;
  }
}
