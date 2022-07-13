export default {
  login: {
    root: "/login",
    passwordRecovery: "/login/password-recovery",
    passwordRecoverySent: "/login/password-recovery-sent",
  },
  dashboard: "/dashboard",
  orders: "/my-orders",
  pay: "/pay",
  balances: {
    root: "/balances",
    subAccounts: "/balances/sub-accounts",
    subAccount: (id: string) => `/balances/sub-accounts/${id}`,
  },
  beneficiaries: {
    root: "/beneficiaries",
    addBeneficiary: "/beneficiaries/add-beneficiary",
  },
  support: "/support",
  exchangeRates: "exchange-rates",
};
