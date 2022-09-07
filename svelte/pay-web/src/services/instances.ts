import config from "../config";
import AuthService from "./auth-service";
import BalanceService from "./balance-service";
import BeneficiaryService from "./beneficiary-service";
import CountryService from "./country-service";
import CurrencyService from "./currency-service";
import TransactionService from "./transaction-service";

export default {
  auth: new AuthService(config.API_BASE_URL),
  beneficiary: new BeneficiaryService(),
  balance: new BalanceService(config.API_BASE_URL),
  transaction: new TransactionService(config.API_BASE_URL),
  currency: new CurrencyService(),
  countries: new CountryService(),
};
