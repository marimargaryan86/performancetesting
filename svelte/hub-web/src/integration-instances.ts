import config from "config/public-config";
import junctionPay from "integration/junction-pay/services";

const junctionPayCompanyService = new junctionPay.CompanyService(
  config.PUBLIC_PAY_ADMIN_API_BASE_URL,
);

export default {
  junctionPay: {
    auth: new junctionPay.AuthenticationService(config.PUBLIC_PAY_ADMIN_API_BASE_URL),
    accounts: new junctionPay.AccountService(config.PUBLIC_PAY_ADMIN_API_BASE_URL),
    companyService: junctionPayCompanyService,
    transactions: new junctionPay.TransactionService(
      config.PUBLIC_PAY_ADMIN_API_BASE_URL,
      junctionPayCompanyService,
    ),
    conversions: new junctionPay.ConversionService(config.PUBLIC_PAY_ADMIN_API_BASE_URL),
  },
};
