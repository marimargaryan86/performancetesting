export default {
  login: "/login",
  dashboard: "/dashboard",
  orders: "/my-orders",
  pay: "/pay",
  balances: {
    root: "/balances",
    subAccounts: "/balances/sub-accounts",
    subAccount: (id: string) => `/balances/sub-accounts/${id}`,
  },
  support: "/support",
  exchangeRates: "exchange-rates",
};
