import type { CountryModel } from "$models/location-models";
import countries from "./data/countries";

export default class CountryService {
  async find(): Promise<CountryModel[]> {
    return countries;
  }
}
