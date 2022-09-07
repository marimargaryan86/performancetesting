import AccountService from "$integration/currency-cloud/services/account-service";
import AuthService from "$integration/currency-cloud/services/auth-service";
import BeneficiaryService from "$integration/currency-cloud/services/beneficiary-service";
import CurrencyService from "$integration/currency-cloud/services/currency-service";
import config from "./config";

const authService = new AuthService(config.CC_API_BASE_URL, config.CC_CLIENT_ID, config.CC_API_KEY);
const beneficiaryService = new BeneficiaryService(config.CC_API_BASE_URL, authService);
const currencyService = new CurrencyService(config.CC_API_BASE_URL, authService);
const accountService = new AccountService(config.CC_API_BASE_URL, authService);

export default {
  beneficiaryService,
  currencyService,
  accountService,
};
