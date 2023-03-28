import { env } from "$env/dynamic/public";
import junctionPay from "integration/junction-pay/services";

const junctionPayCompanyService = new junctionPay.CompanyService(env.PUBLIC_PAY_ADMIN_API_BASE_URL);

export default {
  junctionPay: {
    auth: new junctionPay.AuthenticationService(env.PUBLIC_PAY_ADMIN_API_BASE_URL),
    accounts: new junctionPay.AccountService(env.PUBLIC_PAY_ADMIN_API_BASE_URL),
    companyService: junctionPayCompanyService,
    transactions: new junctionPay.TransactionService(
      env.PUBLIC_PAY_ADMIN_API_BASE_URL,
      junctionPayCompanyService,
    ),
    conversions: new junctionPay.ConversionService(env.PUBLIC_PAY_ADMIN_API_BASE_URL),
    balances: new junctionPay.BalanceService(env.PUBLIC_PAY_ADMIN_API_BASE_URL),
    currencies: new junctionPay.CurrencyService(env.PUBLIC_PAY_API_BASE_URL),
  },
};
