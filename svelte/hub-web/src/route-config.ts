export default {
  home: "/",
  book: {
    root: "/book",
    select: {
      root: "/book/select-offer",
      actions: {
        poll: "/book/select-offer?/poll",
        select: "/book/select-offer?/select",
      },
    },
    passengerDetails: {
      root: "/book/passenger-details",
      actions: {
        createOrder: "/book/passenger-details?/createOrder",
      },
    },
    payment: {
      root: "/book/payment",
      actions: {
        poll: "/book/payment?/poll",
      },
    },
    confirmation: {
      root: "/book/confirmation",
    },
    actions: {
      listPlaces: "/book?/listPlaces",
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
        addBalances: (id: string): string => `/pay/accounts/${id}?/addBalances`,
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
    },
  },
};
