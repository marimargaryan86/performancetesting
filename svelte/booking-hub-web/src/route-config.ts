export default {
  home: "/",
  book: {
    root: "/book",
    select: {
      root: "/book/select-offer",
    },
    passengerDetails: {
      root: "/book/passenger-details",
    },
    payment: {
      root: "/book/payment",
    },
  },
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
      beneficiary: (id?: string): string => `/pay/beneficiaries/${id ?? "add"}`,
      addBeneficiary: "/pay/beneficiaries/add",
      actions: {
        listBeneficiaries: "/pay/beneficiaries?/listBeneficiaries",
      },
    },
  },
  go: {
    root: "/go",
    bookings: {
      root: "/go/bookings",
      refunds: "/go/bookings/refunds",
    },
  },
};
