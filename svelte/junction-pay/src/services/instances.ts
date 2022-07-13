import config from "$src/config";
import AuthService from "./auth-service";
import BalanceService from "./balance-service";
import BeneficiaryService from "./beneficiary-service";
import TransactionService from "./transaction-service";

export default {
  auth: new AuthService(config.API_BASE_URL),
  beneficiary: new BeneficiaryService(config.API_BASE_URL),
  balance: new BalanceService(config.API_BASE_URL),
  transaction: new TransactionService(config.API_BASE_URL),
};
