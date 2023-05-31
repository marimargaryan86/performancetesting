export default {
  home: "/",
  login: "/login",
  settings: "/settings",
  pay: {
    root: "/pay",
    activity: {
      root: "/pay/activity",
      conversions: "/pay/activity/fx",
      actions: {
        getBooking: "/pay/activity?/getBooking",
      },
    },
    accounts: {
      root: "/pay/accounts",
      account: (id: string): string => `/pay/accounts/${id}`,
    },
    beneficiaries: {
      root: "/pay/beneficiaries",
      beneficiary: (id: string): string => `/pay/beneficiaries/${id}`,
      addBeneficiary: "/pay/beneficiaries/add",
    },
  },
};
