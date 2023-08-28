// Trip management
const tripManagementRoot = "/trip-management" as const;
// Trip management - book
const tripManagementBookRoot = `${tripManagementRoot}/book` as const;
const tripManagementBookSelectRoot = `${tripManagementBookRoot}/select-offer` as const;
const tripManagementBookPassengersRoot = `${tripManagementBookRoot}/passenger-details` as const;
const tripManagementBookPaymentRoot = `${tripManagementBookRoot}/payment` as const;
const tripManagementBookConfirmationRoot = `${tripManagementBookRoot}/confirmation` as const;
// Trip management - Orders
const tripManagementOrdersRoot = `${tripManagementRoot}/orders` as const;
// Login
const loginRoot = "/login" as const;
// Settings
const settingsRoot = "/settings" as const;
// Pay
const payRoot = "/pay" as const;
// Pay - activity
const payActivityRoot = `${payRoot}/activity` as const;
const payActivityConversion = `${payActivityRoot}/fx` as const;
// Pay - accounts
const payAccountsRoot = `${payRoot}/accounts` as const;
function payAccountsAccount<TID extends string>(id: TID): `${typeof payAccountsRoot}/${TID}` {
  return `${payAccountsRoot}/${id}`;
}
// Pay - Beneficiaries
const payBeneficiaries = `${payRoot}/beneficiaries` as const;
function payBeneficiariesBeneficiary<
  TID extends string | undefined = undefined,
  TOut = `${typeof payBeneficiaries}/${TID extends undefined ? "add" : TID}`,
>(id?: TID): TOut {
  return `${payBeneficiaries}/${id ?? "add"}` as TOut;
}
// Go
const goRoot = "/go" as const;
// Go - Bookings
const goBookings = `${goRoot}/bookings` as const;

export default {
  home: "/" as const,
  tripManagement: {
    root: tripManagementRoot,
    book: {
      root: tripManagementBookRoot,
      select: {
        root: tripManagementBookSelectRoot,
        actions: {
          poll: `${tripManagementBookSelectRoot}?/poll` as const,
          select: `${tripManagementBookSelectRoot}?/select` as const,
        },
      },
      passengerDetails: {
        root: tripManagementBookPassengersRoot,
        actions: {
          createOrder: `${tripManagementBookPassengersRoot}?/createOrder` as const,
        },
      },
      payment: {
        root: tripManagementBookPaymentRoot,
        actions: {
          poll: `${tripManagementBookPaymentRoot}?/poll` as const,
        },
      },
      confirmation: {
        root: tripManagementBookConfirmationRoot,
      },
      actions: {
        listPlaces: `${tripManagementBookRoot}?/listPlaces` as const,
      },
    },
    orders: {
      root: tripManagementOrdersRoot,
    },
  },
  login: {
    root: loginRoot,
    actions: {
      login: `${loginRoot}?/login` as const,
      logout: `${loginRoot}?/logout` as const,
    },
  },
  settings: settingsRoot,
  pay: {
    root: payRoot,
    activity: {
      root: payActivityRoot,
      conversions: {
        root: payActivityConversion,
        actions: {
          listConversions: `${payActivityConversion}?/listConversions` as const,
        },
      },
      actions: {
        getBooking: `${payActivityRoot}?/getBooking` as const,
        listTransactions: `${payActivityRoot}?/listTransactions` as const,
      },
    },
    accounts: {
      root: payAccountsRoot,
      account: payAccountsAccount,
      actions: {
        listAccounts: `${payAccountsRoot}?/listAccounts` as const,
        addBalances: <TID extends string>(
          id: TID,
        ): `${ReturnType<typeof payAccountsAccount<TID>>}?/addBalances` =>
          `${payAccountsAccount(id)}?/addBalances`,
      },
    },
    beneficiaries: {
      root: payBeneficiaries,
      beneficiary: payBeneficiariesBeneficiary,
      actions: {
        listBeneficiaries: `${payBeneficiaries}?/listBeneficiaries` as const,
      },
    },
  },
  go: {
    root: goRoot,
    bookings: {
      root: goBookings,
    },
  },
};
