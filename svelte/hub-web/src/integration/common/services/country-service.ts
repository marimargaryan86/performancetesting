import type { CountryModel } from "models/location";
import countries from "../data/countries";

export default class CountryService {
  private readonly countries = new Map(countries.map((country) => [country.code, country]));

  findCountries(): Map<string, CountryModel> {
    return this.countries;
  }
}
