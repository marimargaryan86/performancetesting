export default {
  home: "/",
  login: "/login",
  settings: "/settings",
  pay: {
    root: "/pay",
    activity: {
      root: "/pay/activity",
      conversions: {
        root: "/pay/activity/fx",
        actions: {
          listConversions: "/pay/activity/fx?/listConversions",
        },
      },
      actions: {
        getBooking: "/pay/activity?/getBooking",
        listTransactions: "/pay/activity?/listTransactions",
      },
    },
    accounts: {
      root: "/pay/accounts",
      account: (id: string): string => `/pay/accounts/${id}`,
      actions: {
        listAccounts: "/pay/accounts?/listAccounts",
      },
    },
    beneficiaries: {
      root: "/pay/beneficiaries",
      beneficiary: (id: string): string => `/pay/beneficiaries/${id}`,
      addBeneficiary: "/pay/beneficiaries/add",
    },
  },
};
